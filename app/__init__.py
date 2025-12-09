from flask import Flask
import os
from flask_migrate import Migrate
from dotenv import dotenv_values
from app.config.database import db

# Create Flask app
app = Flask(__name__)

# Load environment variables
env_values = dotenv_values(".env")

# Configuration
database_url = os.getenv("DATABASE_URL") or env_values.get("DATABASE_URL") or "postgresql://postgres:postgres@db:5432/compactify_db"
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY") or env_values.get("SECRET_KEY") or "your-secret-key-change-in-production"
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = "app/"

# Initialize database
db.init_app(app)

# Initialize Flask-Migrate
migrate = Migrate(app, db)

# Import routes after app initialization
from app.router import *


