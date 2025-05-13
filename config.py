import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-for-testing'
    
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///eco_route.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    MAPS_API_KEY = os.environ.get('MAPS_API_KEY') or 'your-maps-api-key'
    WEATHER_API_KEY = os.environ.get('WEATHER_API_KEY') or 'your-weather-api-key'
    
    EMISSIONS = {
        'walking': 0,
        'biking': 0,
        'bus': 68,
        'train': 41,
        'car_small': 120,
        'car_medium': 170,
        'car_large': 220,
        'rideshare': 180,
    }