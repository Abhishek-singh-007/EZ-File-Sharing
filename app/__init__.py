from flask import Flask
import mysql.connector
from config import DB_CONFIG
from flask_jwt_extended import JWTManager
import os

def create_app():
    app = Flask(__name__)
    app.config['UPLOAD_FOLDER'] = 'uploads'
    app.secret_key = 'supersecretkey'
    app.config['JWT_SECRET_KEY'] = 'jwt-secret-key'

    # DB Connection
    app.db = mysql.connector.connect(**DB_CONFIG)
    app.cursor = app.db.cursor(dictionary=True)

    # JWT Setup
    jwt = JWTManager(app)

    # Blueprints
    from app.routes.ops_user import ops_routes
    from app.routes.client_user import client_routes

    app.register_blueprint(ops_routes)
    app.register_blueprint(client_routes)

    return app
