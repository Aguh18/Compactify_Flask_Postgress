#!/bin/bash
set -e

echo "🚀 Starting Compactify Application..."

# Function to wait for database
wait_for_db() {
    echo "⏳ Waiting for database connection..."
    until python -c "
import os
import psycopg2
try:
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST', 'db'),
        port=os.getenv('DB_PORT', '5432'),
        user=os.getenv('DB_USER', 'postgres'),
        password=os.getenv('DB_PASSWORD', 'postgres'),
        dbname=os.getenv('DB_NAME', 'compactify_db')
    )
    conn.close()
    print('✅ Database is ready!')
    return True
except psycopg2.OperationalError as e:
    if 'does not exist' in str(e):
        print('❌ Database does not exist, creating...')
        return False
    else:
        print(f'❌ Database error: {e}')
        return False
except Exception as e:
    print(f'❌ Error: {e}')
    return False
except ImportError:
    print('❌ psycopg2 not installed')
    return False
"
do
    sleep 2
done

# Check if database exists
if python -c "
import os
import psycopg2
try:
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST', 'db'),
        port=os.getenv('DB_PORT', '5432'),
        user=os.getenv('DB_USER', 'postgres'),
        password=os.getenv('DB_PASSWORD', 'postgres')
    )

    # Try to connect to the specific database
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST', 'db'),
        port=os.getenv('DB_PORT', '5432'),
        user=os.getenv('DB_USER', 'postgres'),
        password=os.getenv('DB_PASSWORD', 'postgres'),
        dbname=os.getenv('DB_NAME', 'compactify_db')
    )
    conn.close()
    print('✅ Database compactify_db exists!')
except psycopg2.OperationalError as e:
    if 'does not exist' in str(e):
        print('⚠️ Database does not exist, creating...')

        # Connect to postgres database first to create database
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST', 'db'),
            port=os.getenv('DB_PORT', '5432'),
            user=os.getenv('DB_USER', 'postgres'),
            password=os.getenv('DB_PASSWORD', 'postgres')
        )
        conn.autocommit = True

        # Create the database
        with conn.cursor() as cursor:
            cursor.execute('CREATE DATABASE ' + os.getenv('DB_NAME', 'compactify_db') + ';')

        conn.close()
        print('✅ Database compactify_db created successfully!')
    else:
        print(f'❌ Database error: {e}')
        exit 1
except Exception as e:
    print(f'❌ Error: {e}')
    exit 1
"

# Run database migrations
echo "📋 Running database migrations..."
flask db upgrade

# Start the application
echo "🚀 Starting Flask application..."
exec gunicorn --bind 0.0.0.0:5000 --workers 4 --worker-class sync --timeout 120 --max-requests 1000 --max-requests-jitter 100 --access-logfile - --error-logfile - server:app