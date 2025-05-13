from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
import os
import json
from datetime import datetime
from config import Config
from extensions import db, login_manager

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
login_manager.init_app(app)

from models import User, Route, SavedRoute

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

from routes import init_routes

init_routes(app, db)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)