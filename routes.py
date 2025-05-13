from flask import render_template, request, jsonify, session, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from models import User, Route, SavedRoute
from carbon_calculator import calculate_carbon_emissions
import requests
import json

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
            
            user = User.query.filter_by(username=username).first()
            if user:
                flash('Username already exists.')
                return redirect(url_for('register'))
            
            user = User.query.filter_by(email=email).first()
            if user:
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
                                  start=start,
                                  end=end,
                                  route_options=route_options)
            
        return render_template('route_comparison.html')
    
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
        
        route_options = get_route_options(start, end)
        return jsonify(route_options)

def get_route_options(start, end):
    """
    Mock function to generate route options
    In a real app, this would call external mapping APIs
    """
    distance = 10.0 
    
    return {
        'walking': {
            'distance': distance,
            'duration': distance * 12,  
            'emissions': calculate_carbon_emissions('walking', distance),
            'icon': 'walking.png'
        },
        'biking': {
            'distance': distance,
            'duration': distance * 4, 
            'emissions': calculate_carbon_emissions('biking', distance),
            'icon': 'biking.png'
        },
        'bus': {
            'distance': distance * 1.2,  
            'duration': distance * 3 + 10,
            'emissions': calculate_carbon_emissions('bus', distance * 1.2),
            'icon': 'bus.png'
        },
        'train': {
            'distance': distance * 1.3,  
            'duration': distance * 2 + 15,  
            'emissions': calculate_carbon_emissions('train', distance * 1.3),
            'icon': 'train.png'
        },
        'car': {
            'distance': distance,
            'duration': distance * 1.5,  
            'emissions': calculate_carbon_emissions('car_medium', distance),
            'icon': 'car.png'
        },
        'rideshare': {
            'distance': distance,
            'duration': distance * 1.5 + 5,
            'emissions': calculate_carbon_emissions('rideshare', distance),
            'icon': 'rideshare.png'
        }
    }