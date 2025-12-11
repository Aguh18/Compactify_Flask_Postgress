from flask import jsonify
from app.config.database import db
from app import app
from sqlalchemy.exc import OperationalError, DisconnectionError
import time

@app.route('/health')
def health_check():
    """
    Health check endpoint to verify database connectivity
    """
    try:
        # Simple database query to test connection
        db.session.execute('SELECT 1')
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'timestamp': time.time()
        }), 200

    except (OperationalError, DisconnectionError) as e:
        return jsonify({
            'status': 'unhealthy',
            'database': 'disconnected',
            'error': str(e),
            'timestamp': time.time()
        }), 503

    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'database': 'error',
            'error': str(e),
            'timestamp': time.time()
        }), 503

@app.route('/health/ready')
def readiness_check():
    """
    Readiness check for Docker containers
    """
    try:
        # Test database connection
        db.session.execute('SELECT 1')

        return jsonify({
            'status': 'ready',
            'database': 'connected',
            'timestamp': time.time()
        }), 200

    except Exception as e:
        return jsonify({
            'status': 'not_ready',
            'database': 'disconnected',
            'error': str(e),
            'timestamp': time.time()
        }), 503