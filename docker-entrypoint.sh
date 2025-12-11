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

# Start the application with optimized configuration
echo "🚀 Starting Flask application with optimized configuration..."

# Get Gunicorn configuration from environment variables
GUNICORN_WORKERS=${GUNICORN_WORKERS:-1}
GUNICORN_TIMEOUT=${GUNICORN_TIMEOUT:-120}
GUNICORN_MAX_REQUESTS=${GUNICORN_MAX_REQUESTS:-100}
GUNICORN_MAX_REQUESTS_JITTER=${GUNICORN_MAX_REQUESTS_JITTER:-15}
GUNICORN_PRELOAD_APP=${GUNICORN_PRELOAD_APP:-false}
GUNICORN_WORKER_CLASS=${GUNICORN_WORKER_CLASS:-sync}

echo "📊 Gunicorn Configuration:"
echo "  Workers: $GUNICORN_WORKERS"
echo "  Timeout: $GUNICORN_TIMEOUT seconds"
echo "  Max Requests: $GUNICORN_MAX_REQUESTS"
echo "  Preload App: $GUNICORN_PRELOAD_APP"
echo "  Worker Class: $GUNICORN_WORKER_CLASS"

# Build gunicorn command with all optimizations
GUNICORN_CMD="gunicorn \
    --bind 0.0.0.0:5000 \
    --workers $GUNICORN_WORKERS \
    --worker-class $GUNICORN_WORKER_CLASS \
    --timeout $GUNICORN_TIMEOUT \
    --max-requests $GUNICORN_MAX_REQUESTS \
    --max-requests-jitter $GUNICORN_MAX_REQUESTS_JITTER \
    --access-logfile - \
    --error-logfile -"

# Add additional optimizations
if [ -n "$GUNICORN_WORKER_CONNECTIONS" ]; then
    GUNICORN_CMD="$GUNICORN_CMD --worker-connections $GUNICORN_WORKER_CONNECTIONS"
fi

if [ -n "$GUNICORN_WORKER_TMP_DIR" ]; then
    GUNICORN_CMD="$GUNICORN_CMD --worker-tmp-dir $GUNICORN_WORKER_TMP_DIR"
fi

# Add --preload-app if enabled
if [ "$GUNICORN_PRELOAD_APP" = "true" ]; then
    GUNICORN_CMD="$GUNICORN_CMD --preload-app"
fi

GUNICORN_CMD="$GUNICORN_CMD server:app"

exec $GUNICORN_CMD