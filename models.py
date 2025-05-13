from extensions import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    saved_routes = db.relationship('SavedRoute', backref='user', lazy='dynamic')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'

class Route(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    start_location = db.Column(db.String(128), nullable=False)
    end_location = db.Column(db.String(128), nullable=False)
    distance = db.Column(db.Float, nullable=False) 
    saved_routes = db.relationship('SavedRoute', backref='route', lazy='dynamic')
    
    def __repr__(self):
        return f'<Route from {self.start_location} to {self.end_location}>'

class SavedRoute(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    route_id = db.Column(db.Integer, db.ForeignKey('route.id'))
    transport_mode = db.Column(db.String(64), nullable=False)
    carbon_saved = db.Column(db.Float, nullable=False)
    date_saved = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<SavedRoute {self.id} by {self.user_id}>'