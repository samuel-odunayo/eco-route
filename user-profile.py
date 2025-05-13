"""
User Profile Module for Eco-Go
Handles user preferences, achievements, and profile management
"""
from models import User, SavedRoute, db
from datetime import datetime, timedelta
from sqlalchemy import func, and_
import json

class UserProfile:
    """Manages user profile information and statistics"""
    
    def __init__(self, user_id):
        self.user_id = user_id
    
    def get_basic_info(self):
        """Get basic user information"""
        user = User.query.get(self.user_id)
        if not user:
            return None
            
        return {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'created_at': user.created_at.strftime('%Y-%m-%d')
        }
    
    def get_carbon_stats(self):
        """Get user's carbon savings statistics"""

        total_saved = db.session.query(func.sum(SavedRoute.carbon_saved))\
            .filter(SavedRoute.user_id == self.user_id)\
            .scalar() or 0
            
        transport_counts = db.session.query(
            SavedRoute.transport_mode, 
            func.count(SavedRoute.id)
        )\
        .filter(SavedRoute.user_id == self.user_id)\
        .group_by(SavedRoute.transport_mode)\
        .all()
        
        transport_modes = {mode: count for mode, count in transport_counts}
        
        monthly_data = self._get_monthly_carbon_data()
        
        
        tree_days = total_saved / (21000 / 365)
        car_km = total_saved / 170
        
        return {
            'total_carbon_saved': total_saved,
            'total_routes': sum(transport_modes.values()),
            'transport_modes': transport_modes,
            'monthly_data': monthly_data,
            'environmental_impact': {
                'tree_days': tree_days,
                'car_km_equivalent': car_km,
                'carbon_kg': total_saved / 1000
            }
        }
    
    def _get_monthly_carbon_data(self):
        """Get carbon savings data by month for the past year"""
        
        start_date = datetime.now() - timedelta(days=365)
        
        monthly_data = db.session.query(
            func.strftime('%Y-%m', SavedRoute.date_saved).label('month'),
            func.sum(SavedRoute.carbon_saved).label('carbon_saved')
        )\
        .filter(and_(
            SavedRoute.user_id == self.user_id,
            SavedRoute.date_saved >= start_date
        ))\
        .group_by('month')\
        .order_by('month')\
        .all()
        
        return {month: float(carbon_saved) for month, carbon_saved in monthly_data}
    
    def get_recent_routes(self, limit=5):
        """Get user's most recent routes"""
        recent_routes = SavedRoute.query\
            .filter(SavedRoute.user_id == self.user_id)\
            .order_by(SavedRoute.date_saved.desc())\
            .limit(limit)\
            .all()
            
        return [self._format_route(route) for route in recent_routes]
    
    def _format_route(self, route):
        """Format route data for API response"""
        return {
            'id': route.id,
            'start': route.route.start_location,
            'end': route.route.end_location,
            'distance': route.route.distance,
            'transport_mode': route.transport_mode,
            'carbon_saved': route.carbon_saved,
            'date': route.date_saved.strftime('%Y-%m-%d')
        }
    
    def get_achievements(self):
        """Get user's environmental achievements"""
        stats = self.get_carbon_stats()
        
        achievements = []
        
        carbon_kg = stats['total_carbon_saved'] / 1000
        if carbon_kg >= 1:
            achievements.append({
                'id': 'carbon_1kg',
                'name': 'Carbon Cutter',
                'description': 'Save 1kg of carbon emissions',
                'unlocked': True,
                'icon': 'leaf'
            })
        if carbon_kg >= 10:
            achievements.append({
                'id': 'carbon_10kg',
                'name': 'Climate Guardian',
                'description': 'Save 10kg of carbon emissions',
                'unlocked': True,
                'icon': 'tree'
            })
        if carbon_kg >= 100:
            achievements.append({
                'id': 'carbon_100kg',
                'name': 'Earth Defender',
                'description': 'Save 100kg of carbon emissions',
                'unlocked': True,
                'icon': 'globe'
            })
            
        route_count = stats['total_routes']
        if route_count >= 5:
            achievements.append({
                'id': 'routes_5',
                'name': 'Eco Commuter',
                'description': 'Take 5 eco-friendly routes',
                'unlocked': True,
                'icon': 'route'
            })
        if route_count >= 20:
            achievements.append({
                'id': 'routes_20',
                'name': 'Green Navigator',
                'description': 'Take 20 eco-friendly routes',
                'unlocked': True,
                'icon': 'compass'
            })
        if route_count >= 50:
            achievements.append({
                'id': 'routes_50',
                'name': 'Sustainable Explorer',
                'description': 'Take 50 eco-friendly routes',
                'unlocked': True,
                'icon': 'map-marked'
            })
            
        if stats['transport_modes'].get('walking', 0) >= 5:
            achievements.append({
                'id': 'walking_5',
                'name': 'Walker',
                'description': 'Walk for 5 journeys',
                'unlocked': True,
                'icon': 'walking'
            })
        if stats['transport_modes'].get('biking', 0) >= 5:
            achievements.append({
                'id': 'biking_5',
                'name': 'Cyclist',
                'description': 'Cycle for 5 journeys',
                'unlocked': True,
                'icon': 'bicycle'
            })
        if stats['transport_modes'].get('bus', 0) >= 5:
            achievements.append({
                'id': 'bus_5',
                'name': 'Bus Patron',
                'description': 'Take the bus for 5 journeys',
                'unlocked': True,
                'icon': 'bus'
            })
        if stats['transport_modes'].get('train', 0) >= 5:
            achievements.append({
                'id': 'train_5',
                'name': 'Train Traveler',
                'description': 'Take the train for 5 journeys',
                'unlocked': True,
                'icon': 'train'
            })
            
        all_achievements = self._get_all_achievements()
        unlocked_ids = [a['id'] for a in achievements]
        
        for achievement in all_achievements:
            if achievement['id'] not in unlocked_ids:
                achievement['unlocked'] = False
                achievements.append(achievement)
                
        return sorted(achievements, key=lambda x: (not x['unlocked'], x['name']))
    
    def _get_all_achievements(self):
        """Get list of all possible achievements"""
        return [
            {
                'id': 'carbon_1kg',
                'name': 'Carbon Cutter',
                'description': 'Save 1kg of carbon emissions',
                'icon': 'leaf'
            },
            {
                'id': 'carbon_10kg',
                'name': 'Climate Guardian',
                'description': 'Save 10kg of carbon emissions',
                'icon': 'tree'
            },
            {
                'id': 'carbon_100kg',
                'name': 'Earth Defender',
                'description': 'Save 100kg of carbon emissions',
                'icon': 'globe'
            },
            {
                'id': 'routes_5',
                'name': 'Eco Commuter',
                'description': 'Take 5 eco-friendly routes',
                'icon': 'route'
            },
            {
                'id': 'routes_20',
                'name': 'Green Navigator',
                'description': 'Take 20 eco-friendly routes',
                'icon': 'compass'
            },
            {
                'id': 'routes_50',
                'name': 'Sustainable Explorer',
                'description': 'Take 50 eco-friendly routes',
                'icon': 'map-marked'
            },
            {
                'id': 'walking_5',
                'name': 'Walker',
                'description': 'Walk for 5 journeys',
                'icon': 'walking'
            },
            {
                'id': 'biking_5',
                'name': 'Cyclist',
                'description': 'Cycle for 5 journeys',
                'icon': 'bicycle'
            },
            {
                'id': 'bus_5',
                'name': 'Bus Patron',
                'description': 'Take the bus for 5 journeys',
                'icon': 'bus'
            },
            {
                'id': 'train_5',
                'name': 'Train Traveler',
                'description': 'Take the train for 5 journeys',
                'icon': 'train'
            },
            {
                'id': 'streak_7',
                'name': 'Weekly Warrior',
                'description': 'Use eco-friendly transport for 7 days in a row',
                'icon': 'calendar-check'
            },
            {
                'id': 'streak_30',
                'name': 'Eco Enthusiast',
                'description': 'Use eco-friendly transport for 30 days in a row',
                'icon': 'calendar-alt'
            }
        ]
    
    def update_preferences(self, preferences):
        """Update user preferences"""
        user = User.query.get(self.user_id)
        if not user:
            return False
            
        if not hasattr(user, 'user_preferences') or not user.user_preferences:
            user.user_preferences = json.dumps(preferences)
        else:
            current_prefs = json.loads(user.user_preferences)
            updated_prefs = {**current_prefs, **preferences}
            user.user_preferences = json.dumps(updated_prefs)
            
        db.session.commit()
        return True
    
    def get_preferences(self):
        """Get user preferences"""
        user = User.query.get(self.user_id)
        if not user or not hasattr(user, 'user_preferences') or not user.user_preferences:

            return {
                'default_transport_mode': 'walking',
                'carbon_display_unit': 'g',
                'distance_unit': 'km',
                'theme': 'light'
            }
            
        return json.loads(user.user_preferences)
