#!/bin/bash
set -e

echo "🚀 Starting Compactify Application..."

# Function to wait for database
wait_for_db() {
    echo "⏳ Waiting for database connection..."
    until python3 -c "
import os
import sys
try:
    import psycopg2
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST', 'db'),
        port=os.getenv('DB_PORT', '5432'),
        user=os.getenv('DB_USER', 'postgres'),
        password=os.getenv('DB_PASSWORD', 'postgres'),
        dbname=os.getenv('DB_NAME', 'compactify_db')
    )
    conn.close()
    print('✅ Database is ready!')
    sys.exit(0)
except psycopg2.OperationalError as e:
    if 'does not exist' in str(e):
        print('❌ Database does not exist, creating...')
        sys.exit(0)
    else:
        print(f'❌ Database error: {e}')
        sys.exit(1)
except Exception as e:
    print(f'❌ Error: {e}')
    sys.exit(1)
"
do
    sleep 2
done
}

# Wait for database to be ready
wait_for_db

# Check if database exists and create if needed
echo "🔍 Checking database existence..."
python3 -c "
import os
import sys
try:
    import psycopg2

    # Connect to postgres database first
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST', 'db'),
        port=os.getenv('DB_PORT', '5432'),
        user=os.getenv('DB_USER', 'postgres'),
        password=os.getenv('DB_PASSWORD', 'postgres')
    )
    conn.autocommit = True

    # Check if database exists
    with conn.cursor() as cursor:
        cursor.execute('SELECT 1 FROM pg_database WHERE datname = %s', (os.getenv('DB_NAME', 'compactify_db'),))
        exists = cursor.fetchone()

        if not exists:
            print('⚠️ Database does not exist, creating...')
            cursor.execute('CREATE DATABASE ' + os.getenv('DB_NAME', 'compactify_db'))
            print('✅ Database created successfully!')
        else:
            print('✅ Database already exists!')

    conn.close()

except Exception as e:
    print(f'❌ Database setup error: {e}')
    sys.exit(1)
"

# Run database migrations
echo "📋 Running database migrations..."
flask db upgrade

# Start the application
echo "🚀 Starting Flask application..."
exec gunicorn --bind 0.0.0.0:5000 --workers 4 --worker-class sync --timeout 120 --max-requests 1000 --max-requests-jitter 100 --access-logfile - --error-logfile - server:app