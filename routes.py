from flask import render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from models import User, Route, SavedRoute
from carbon_calculator import calculate_carbon_emissions
import requests
import json

def geocode(address):
    """Convert address to (lat, lng) using free Nominatim API"""
    try:
        res = requests.get(
            'https://nominatim.openstreetmap.org/search',
            params={'q': address, 'format': 'json', 'limit': 1},
            headers={'User-Agent': 'eco-route-app'},
            timeout=5
        )
        data = res.json()
        if data:
            return (float(data[0]['lat']), float(data[0]['lon']))
    except Exception:
        pass
    return None

def get_osrm_route(start, end, mode):
    """Get real distance/duration from OSRM free routing API"""
    osrm_mode = {
        'walking': 'foot', 'biking': 'bike',
        'car': 'car', 'bus': 'car', 'train': 'car', 'rideshare': 'car'
    }.get(mode, 'car')
    try:
        url = f"https://router.project-osrm.org/route/v1/{osrm_mode}/{start[1]},{start[0]};{end[1]},{end[0]}"
        res = requests.get(url, params={'overview': 'false'}, timeout=5)
        data = res.json()
        if data.get('code') == 'Ok':
            route = data['routes'][0]
            return {
                'distance': round(route['distance'] / 1000, 2),  # km
                'duration': round(route['duration'] / 60, 1)     # minutes
            }
    except Exception:
        pass
    return None

def get_route_options(start, end):
    """Get real route options using geocoding + OSRM"""
    start_coords = geocode(start)
    end_coords = geocode(end)

    if not start_coords or not end_coords:
        # Fallback to placeholder if geocoding fails
        return _fallback_route_options()

    modes = {
        'walking': 'walking',
        'biking': 'biking',
        'bus': 'bus',
        'train': 'train',
        'car': 'car',
        'rideshare': 'rideshare'
    }

    results = {}
    for mode, carbon_key in [
        ('walking', 'walking'), ('biking', 'biking'),
        ('bus', 'bus'), ('train', 'train'),
        ('car', 'car_medium'), ('rideshare', 'rideshare')
    ]:
        data = get_osrm_route(start_coords, end_coords, mode)
        if data:
            results[mode] = {
                'distance': data['distance'],
                'duration': data['duration'],
                'emissions': calculate_carbon_emissions(carbon_key, data['distance'])
            }

    return results if results else _fallback_route_options()

def _fallback_route_options():
    """Used when geocoding/OSRM fails"""
    distance = 10.0
    return {
        'walking':  {'distance': distance, 'duration': distance * 12, 'emissions': calculate_carbon_emissions('walking', distance)},
        'biking':   {'distance': distance, 'duration': distance * 4,  'emissions': calculate_carbon_emissions('biking', distance)},
        'bus':      {'distance': distance * 1.2, 'duration': distance * 3 + 10, 'emissions': calculate_carbon_emissions('bus', distance * 1.2)},
        'train':    {'distance': distance * 1.3, 'duration': distance * 2 + 15, 'emissions': calculate_carbon_emissions('train', distance * 1.3)},
        'car':      {'distance': distance, 'duration': distance * 1.5, 'emissions': calculate_carbon_emissions('car_medium', distance)},
        'rideshare':{'distance': distance, 'duration': distance * 1.5 + 5, 'emissions': calculate_carbon_emissions('rideshare', distance)},
    }

def init_routes(app, db):
    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            username = request.form.get('username')
            email = request.form.get('email')
            password = request.form.get('password')

            if User.query.filter_by(username=username).first():
                flash('Username already exists.')
                return redirect(url_for('register'))
            if User.query.filter_by(email=email).first():
                flash('Email already exists.')
                return redirect(url_for('register'))

            new_user = User(username=username, email=email)
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()

            flash('Registration successful! Please log in.')
            return redirect(url_for('login'))
        return render_template('register.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            user = User.query.filter_by(username=username).first()
            if user and user.check_password(password):
                login_user(user)
                return redirect(url_for('dashboard'))
            flash('Invalid username or password.')
        return render_template('login.html')

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        return redirect(url_for('index'))

    @app.route('/dashboard')
    @login_required
    def dashboard():
        saved_routes = SavedRoute.query.filter_by(user_id=current_user.id).all()
        total_carbon_saved = sum([route.carbon_saved for route in saved_routes])
        return render_template('dashboard.html',
                               saved_routes=saved_routes,
                               total_carbon_saved=total_carbon_saved)

    @app.route('/route', methods=['GET', 'POST'])
    def route_comparison():
        if request.method == 'POST':
            start = request.form.get('start')
            end = request.form.get('end')
            route_options = get_route_options(start, end)
            return render_template('route_comparison.html',
                                   start=start, end=end,
                                   route_options=route_options)
        return render_template('route_comparison.html')

    @app.route('/profile')
    @login_required
    def profile():
        saved_routes = SavedRoute.query.filter_by(user_id=current_user.id).all()
        total_carbon_saved = sum(r.carbon_saved for r in saved_routes)
        total_routes = len(saved_routes)

        transport_modes = {}
        for r in saved_routes:
            transport_modes[r.transport_mode] = transport_modes.get(r.transport_mode, 0) + 1

        carbon_kg = total_carbon_saved / 1000

        all_achievements = [
            {'id': 'carbon_1kg',  'name': 'Carbon Cutter',       'description': 'Save 1kg of CO2',              'unlocked': carbon_kg >= 1},
            {'id': 'carbon_10kg', 'name': 'Climate Guardian',     'description': 'Save 10kg of CO2',             'unlocked': carbon_kg >= 10},
            {'id': 'carbon_100kg','name': 'Earth Defender',       'description': 'Save 100kg of CO2',            'unlocked': carbon_kg >= 100},
            {'id': 'routes_5',    'name': 'Eco Commuter',         'description': 'Take 5 eco-friendly routes',   'unlocked': total_routes >= 5},
            {'id': 'routes_20',   'name': 'Green Navigator',      'description': 'Take 20 eco-friendly routes',  'unlocked': total_routes >= 20},
            {'id': 'routes_50',   'name': 'Sustainable Explorer', 'description': 'Take 50 eco-friendly routes',  'unlocked': total_routes >= 50},
            {'id': 'walking_5',   'name': 'Walker',               'description': 'Walk for 5 journeys',          'unlocked': transport_modes.get('walking', 0) >= 5},
            {'id': 'biking_5',    'name': 'Cyclist',              'description': 'Cycle for 5 journeys',         'unlocked': transport_modes.get('biking', 0) >= 5},
            {'id': 'bus_5',       'name': 'Bus Patron',           'description': 'Take the bus for 5 journeys',  'unlocked': transport_modes.get('bus', 0) >= 5},
            {'id': 'train_5',     'name': 'Train Traveler',       'description': 'Take the train for 5 journeys','unlocked': transport_modes.get('train', 0) >= 5},
        ]

        carbon_stats = {
            'total_carbon_saved': total_carbon_saved,
            'total_routes': total_routes,
            'transport_modes': transport_modes,
            'carbon_offset': round(carbon_kg, 2),
            'energy_saved': round(carbon_kg * 3.6, 2),
        }

        unlocked = sum(1 for a in all_achievements if a['unlocked'])

        return render_template('profile.html',
                               carbon_stats=carbon_stats,
                               achievements=all_achievements,
                               unlocked_achievements=unlocked,
                               total_achievements=len(all_achievements))

    @app.route('/profile/update', methods=['POST'])
    @login_required
    def update_profile():
        username = request.form.get('username')
        if username and username != current_user.username:
            if User.query.filter_by(username=username).first():
                flash('Username already taken.')
            else:
                current_user.username = username
                db.session.commit()
                flash('Profile updated successfully.')
        return redirect(url_for('profile'))

    @app.route('/api/save_route', methods=['POST'])
    @login_required
    def save_route():
        data = request.get_json()
        start = data.get('start')
        end = data.get('end')
        distance = data.get('distance')
        transport_mode = data.get('transport_mode')
        carbon_saved = data.get('carbon_saved')

        route = Route.query.filter_by(start_location=start, end_location=end).first()
        if not route:
            route = Route(start_location=start, end_location=end, distance=distance)
            db.session.add(route)
            db.session.commit()

        saved_route = SavedRoute(
            user_id=current_user.id,
            route_id=route.id,
            transport_mode=transport_mode,
            carbon_saved=carbon_saved
        )
        db.session.add(saved_route)
        db.session.commit()
        return jsonify({'success': True})

    @app.route('/api/route_options', methods=['GET'])
    def api_route_options():
        start = request.args.get('start')
        end = request.args.get('end')
        if not start or not end:
            return jsonify({'error': 'Missing start or end parameters'}), 400
        return jsonify(get_route_options(start, end))
