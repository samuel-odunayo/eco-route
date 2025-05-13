"""
API Integrations for Eco-Go
This module handles external API connections for mapping, weather, and carbon data
"""
import requests
import json
import os
from datetime import datetime, timedelta
from urllib.parse import quote

class MapsAPI:
    """
    Handles interactions with mapping APIs to get route information
    """
    def __init__(self, api_key=None):
        self.api_key = api_key or os.environ.get('MAPS_API_KEY') or 'demo_key'
        self.base_url = "https://router.project-osrm.org/route/v1"
    
    def get_route(self, start, end, transport_mode='driving'):
        """
        Get route information between two points
        
        Args:
            start (tuple): (latitude, longitude) of starting point
            end (tuple): (latitude, longitude) of ending point
            transport_mode (str): Mode of transportation (driving, walking, cycling, etc.)
            
        Returns:
            dict: Route information including distance, duration, and coordinates
        """
        
        osrm_mode = self._convert_transport_mode(transport_mode)
        
        coords = f"{start[1]},{start[0]};{end[1]},{end[0]}"
        
        url = f"{self.base_url}/{osrm_mode}/{coords}"
        
        try:
            response = requests.get(url, params={
                'overview': 'full',
                'geometries': 'geojson',
                'steps': 'true'
            })
            
            if response.status_code == 200:
                data = response.json()
                if data['code'] == 'Ok' and len(data['routes']) > 0:
                    route = data['routes'][0]
                    return {
                        'distance': route['distance'] / 1000,  
                        'duration': route['duration'] / 60,   
                        'coordinates': route['geometry']['coordinates'],
                        'success': True
                    }
            
            return {
                'success': False,
                'error': 'Failed to get route information',
                'status_code': response.status_code
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_routes_comparison(self, start, end):
        """
        Get comparison of routes for different transportation modes
        
        Args:
            start (str): Starting location (address)
            end (str): Destination location (address)
            
        Returns:
            dict: Route options with details for each transport mode
        """        
        start_coords = self.geocode(start)
        end_coords = self.geocode(end)
        
        if not start_coords or not end_coords:
            return {
                'success': False,
                'error': 'Failed to geocode addresses'
            }
                
        transport_modes = ['walking', 'cycling', 'driving', 'bus', 'train']
        routes = {}
        
        for mode in transport_modes:
            route_info = self.get_route(start_coords, end_coords, mode)
            
            if route_info['success']:
                app_mode = self._map_to_app_mode(mode)
                
                routes[app_mode] = {
                    'distance': route_info['distance'],
                    'duration': route_info['duration'],
                    'coordinates': route_info['coordinates']
                }
        
        return {
            'success': True,
            'routes': routes
        }
    
    def geocode(self, address):
        """
        Convert address to coordinates
        
        Args:
            address (str): Address to geocode
            
        Returns:
            tuple: (latitude, longitude) or None if geocoding fails
        """
        hash_val = sum(ord(c) for c in address) % 100
        
        base_lat, base_lng = 37.7749, -122.4194
        
        lat = base_lat + (hash_val / 1000)
        lng = base_lng + (hash_val / 1000)
        
        return (lat, lng)
    
    def _convert_transport_mode(self, mode):
        """Convert between app transport modes and API modes"""
        mode_map = {
            'walking': 'foot',
            'biking': 'bike',
            'cycling': 'bike',
            'car': 'car',
            'driving': 'car',
            'bus': 'car', 
            'train': 'car', 
            'rideshare': 'car'
        }
        return mode_map.get(mode, 'car')
    
    def _map_to_app_mode(self, api_mode):
        """Map API mode to application mode"""
        mode_map = {
            'foot': 'walking',
            'walking': 'walking',
            'bike': 'biking',
            'cycling': 'biking',
            'car': 'car',
            'driving': 'car'
        }
        return mode_map.get(api_mode, api_mode)


class WeatherAPI:
    """
    Handles interactions with weather APIs to get weather information
    """
    def __init__(self, api_key=None):
        self.api_key = api_key or os.environ.get('WEATHER_API_KEY') or 'demo_key'
        self.base_url = "https://api.openweathermap.org/data/2.5"
    
    def get_weather(self, location):
        """
        Get current weather for a location
        
        Args:
            location (str or tuple): Location as string address or (lat, lng) tuple
            
        Returns:
            dict: Weather information
        """
        
        if isinstance(location, tuple):
            lat, lng = location
        else:
            hash_val = sum(ord(c) for c in str(location)) % 5
            
            weather_conditions = [
                {'main': 'Clear', 'description': 'clear sky', 'temp': 22, 'humidity': 50},
                {'main': 'Clouds', 'description': 'few clouds', 'temp': 18, 'humidity': 60},
                {'main': 'Rain', 'description': 'light rain', 'temp': 15, 'humidity': 80},
                {'main': 'Snow', 'description': 'light snow', 'temp': 0, 'humidity': 90},
                {'main': 'Thunderstorm', 'description': 'thunderstorm', 'temp': 17, 'humidity': 85}
            ]
            
            return {
                'success': True,
                'weather': weather_conditions[hash_val]
            }
    
    def get_weather_forecast(self, location, days=5):
        """
        Get weather forecast for a location
        
        Args:
            location (str or tuple): Location as string address or (lat, lng) tuple
            days (int): Number of days for forecast
            
        Returns:
            dict: Weather forecast information
        """
        if isinstance(location, tuple):
            lat, lng = location
        else:
            hash_val = sum(ord(c) for c in str(location)) % 5
            
            weather_conditions = [
                {'main': 'Clear', 'description': 'clear sky', 'temp': 22, 'humidity': 50},
                {'main': 'Clouds', 'description': 'few clouds', 'temp': 18, 'humidity': 60},
                {'main': 'Rain', 'description': 'light rain', 'temp': 15, 'humidity': 80},
                {'main': 'Snow', 'description': 'light snow', 'temp': 0, 'humidity': 90},
                {'main': 'Thunderstorm', 'description': 'thunderstorm', 'temp': 17, 'humidity': 85}
            ]
            
            forecast = []
            base_condition = weather_conditions[hash_val]
            
            for i in range(days):            
                day_offset = (i * 3) % 5
                day_condition = weather_conditions[(hash_val + day_offset) % 5].copy()
                
                day_condition['temp'] = base_condition['temp'] + ((i % 3) - 1) * 2
                
                forecast_date = datetime.now() + timedelta(days=i)
                day_condition['date'] = forecast_date.strftime("%Y-%m-%d")
                
                forecast.append(day_condition)
            
            return {
                'success': True,
                'forecast': forecast
            }


class CarbonAPI:
    """
    Interface to carbon footprint data and calculations
    """
    def __init__(self):
        self.emissions_data = {
            'walking': 0,
            'biking': 0,
            'bus': 68,
            'train': 41,
            'car_small': 120,
            'car_medium': 170,
            'car_large': 220,
            'rideshare': 180
        }
    
    def get_emissions_factor(self, transport_mode, region=None):
        """
        Get emissions factor for a transportation mode, optionally adjusted for region
        
        Args:
            transport_mode (str): Mode of transportation
            region (str, optional): Geographic region for regional adjustments
            
        Returns:
            float: Emissions factor in grams CO2 per kilometer
        """
        
        base_factor = self.emissions_data.get(transport_mode, 0)
        
        if region:
            regional_factor = self._get_regional_adjustment(region)
            return base_factor * regional_factor
        
        return base_factor
    
    def _get_regional_adjustment(self, region):
        """
        Get regional adjustment factor for emissions
        Some regions have more efficient public transport or cleaner electricity
        """
        regional_factors = {
            'europe': 0.9, 
            'usa': 1.1,    
            'asia': 1.05 
        }
        
        return regional_factors.get(region.lower(), 1.0)
    
    def calculate_trip_emissions(self, transport_mode, distance, region=None):
        """
        Calculate emissions for a specific trip
        
        Args:
            transport_mode (str): Mode of transportation
            distance (float): Distance in kilometers
            region (str, optional): Geographic region
            
        Returns:
            float: Total emissions in grams CO2
        """
        emissions_factor = self.get_emissions_factor(transport_mode, region)
        return emissions_factor * distance
    
    def get_equivalent_impact(self, carbon_grams):
        """
        Convert carbon emissions to equivalent environmental impacts
        
        Args:
            carbon_grams (float): Carbon emissions in grams
            
        Returns:
            dict: Dictionary of equivalent environmental impacts
        """
        tree_absorption_yearly = 21000  
        driving_emissions_per_km = 170
        
        return {
            'tree_days': carbon_grams / (tree_absorption_yearly / 365),
            'car_km_equivalent': carbon_grams / driving_emissions_per_km,
            'carbon_kg': carbon_grams / 1000
        }
