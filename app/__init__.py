import os

from dotenv import dotenv_values
from flask import Flask
from flask_migrate import Migrate

from app.config.database import db

app = Flask(__name__)
env_values = dotenv_values(".env")


# Auto-detect Docker environment and override database host
def get_database_url():
    """
    Get database URL with smart Docker detection.
    If running in Docker, override DB_HOST from .env to use 'db' service name.
    """
    # Check if running in Docker
    is_docker = os.path.exists("/.dockerenv")

    # Get database URL from environment or .env
    db_url = os.getenv("DATABASE_URL") or env_values.get("DATABASE_URL")

    if db_url and is_docker:
        # Parse and rebuild URL with correct Docker hostname
        # Replace localhost or any custom host with 'db' (Docker service name)
        if "localhost" in db_url or "127.0.0.1" in db_url:
            db_url = db_url.replace("localhost", "db").replace("127.0.0.1", "db")
            # Also fix port if it's custom
            if ":4111" in db_url:
                db_url = db_url.replace(":4111", ":5432")
            print(
                f"[INFO] Running in Docker - Updated DATABASE_URL to use 'db' service"
            )
        return db_url
    elif db_url:
        print(f"[INFO] Running locally - Using DATABASE_URL from .env")
        return db_url
    else:
        # Fallback default
        if is_docker:
            print("[INFO] Running in Docker - Using default Docker DATABASE_URL")
            return "postgresql://postgres:postgres@db:5432/compactify_db"
        else:
            print("[INFO] Running locally - Using default local DATABASE_URL")
            return "postgresql://postgres:postgres@localhost:5432/compactify_db"


database_url = get_database_url()
app.config["SECRET_KEY"] = (
    os.getenv("SECRET_KEY")
    or env_values.get("SECRET_KEY")
    or "your-secret-key-change-in-production"
)
app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["UPLOAD_FOLDER"] = "app/"

# Database connection pooling and retry configuration for long-running containers
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_size": 10,
    "pool_recycle": 280,  # Recycle connections every 280 seconds (before 5min timeout)
    "pool_pre_ping": True,  # Validate connections before use
    "pool_timeout": 30,  # Timeout when getting connection from pool
    "max_overflow": 20,  # Allow additional connections beyond pool_size
    "connect_args": {
        "connect_timeout": 10,  # Connection timeout in seconds
        "application_name": "compactify_app",  # Identify application in PostgreSQL logs
    },
}

db.init_app(app)
migrate = Migrate(app, db)
from app import health  # Import health endpoints
from app.router import *

# Track if app has been initialized
_app_initialized = False


def preload_models():
    """Preload heavy models at startup to prevent first-request delays"""
    try:
        import threading

        from app.controllers.removeBgController import preload_rembg_model

        # Start model preloading in background thread
        threading.Thread(target=preload_rembg_model, daemon=True).start()
        print("Background model preloading started...")

    except Exception as e:
        print(f"Failed to start model preloading: {e}")


@app.before_request
def initialize_app():
    """Initialize application components on first request"""
    global _app_initialized
    if not _app_initialized:
        try:
            # Create database tables if they don't exist
            with app.app_context():
                db.create_all()

            _app_initialized = True
            print("Application initialized successfully")

        except Exception as e:
            print(f"Application initialization error: {e}")

    # Universal model preload - trigger on any user request
    universal_model_preload()


# Universal model preload function
def universal_model_preload():
    """Preload rembg model when any user accesses the application"""
    try:
        import threading

        from flask import request  # Import request here

        from app.controllers.removeBgController import (
            _rembg_model_loaded,
            preload_rembg_model,
        )

        # Skip preload for static files and API calls
        if any(
            path in request.path
            for path in [
                "/static/",
                "/health",
                "/favicon",
                ".css",
                ".js",
                ".png",
                ".jpg",
            ]
        ):
            return

        # Check if model is not loaded
        if not _rembg_model_loaded:
            # Start preloading in background thread (non-blocking)
            print(
                f"[*] User hit {request.path} - starting universal rembg model preload..."
            )
            threading.Thread(target=preload_rembg_model, daemon=True).start()
        else:
            print(f"[*] User hit {request.path} - rembg model already loaded")

    except Exception as e:
        print(f"[*] Universal preload error (non-critical): {e}")


# Disable auto preloading to save memory - use universal preload instead
# preload_models()  # Replaced with universal preload
