from flask import Flask
import os
from flask_migrate import Migrate
from dotenv import dotenv_values
from app.config.database import db
app = Flask(__name__)
env_values = dotenv_values(".env")
database_url = os.getenv("DATABASE_URL") or env_values.get("DATABASE_URL") or "postgresql://postgres:postgres@db:5432/compactify_db"
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY") or env_values.get("SECRET_KEY") or "your-secret-key-change-in-production"
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = "app/"

# Database connection pooling and retry configuration for long-running containers
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_size': 10,
    'pool_recycle': 280,  # Recycle connections every 280 seconds (before 5min timeout)
    'pool_pre_ping': True,  # Validate connections before use
    'pool_timeout': 30,  # Timeout when getting connection from pool
    'max_overflow': 20,  # Allow additional connections beyond pool_size
    'connect_args': {
        'connect_timeout': 10,  # Connection timeout in seconds
        'application_name': 'compactify_app'  # Identify application in PostgreSQL logs
    }
}

db.init_app(app)
migrate = Migrate(app, db)
from app.router import *
from app import health  # Import health endpoints