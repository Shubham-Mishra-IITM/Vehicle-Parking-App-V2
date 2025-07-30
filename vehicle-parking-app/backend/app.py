from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from redis import Redis
from config import Config
from dotenv import load_dotenv
from database import db
import os

# Change to the backend directory to ensure correct paths
backend_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(backend_dir)

# Load environment variables from .env file
load_dotenv()

# Create Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Print debug information
print(f"🔍 Debug Info:")
print(f"   Working Directory: {os.getcwd()}")
print(f"   Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
print(f"   Database File: {db_path}")
print(f"   File Exists: {os.path.exists(db_path)}")
print(f"   Directory Exists: {os.path.exists(os.path.dirname(db_path))}")

# Ensure the instance folder exists
instance_path = os.path.join(backend_dir, 'instance')
os.makedirs(instance_path, exist_ok=True)

# Initialize database with app
db.init_app(app)

# Import models after db is set up
from models.user import User
from models.parking_lot import ParkingLot  
from models.parking_spot import ParkingSpot
from models.reservation import Reservation

# Initialize Redis
try:
    redis = Redis(host=Config.REDIS_HOST, port=Config.REDIS_PORT, decode_responses=True)
    # Test Redis connection
    redis.ping()
    print("✅ Redis connected successfully!")
except Exception as e:
    print(f"⚠️  Redis connection failed: {e}")
    redis = None

# Enable CORS
CORS(app)

# Initialize Celery with Flask app
try:
    from tasks.celery_app import make_celery
    celery = make_celery(app.import_name)
    
    # Ensure correct Redis URL for local development
    celery.conf.update(
        broker_url='redis://localhost:6379/1',
        result_backend='redis://localhost:6379/1'
    )
    
    app.celery = celery  # Make Celery available to the Flask app
    print("✅ Celery initialized with Flask app!")
    print(f"✅ Celery broker: {celery.conf.broker_url}")
except Exception as e:
    print(f"⚠️  Celery initialization failed: {e}")
    celery = None
    app.celery = None

# Register routes
try:
    from routes import register_routes
    register_routes(app)
    print("✅ Routes registered successfully!")
except ImportError as e:
    print(f"⚠️  Routes registration failed: {e}")

@app.route('/')
def index():
    """Health check endpoint"""
    return {
        'message': 'Vehicle Parking App API is running!',
        'version': '2.0',
        'status': 'healthy',
        'database': 'connected',
        'redis': 'connected' if redis else 'disconnected'
    }

@app.route('/debug-db')
def debug_db():
    """Debug database connection"""
    import os
    try:
        db_uri = app.config['SQLALCHEMY_DATABASE_URI']
        db_path = db_uri.replace('sqlite:///', '') if db_uri.startswith('sqlite:///') else 'unknown'
        
        from models.user import User
        users = User.query.all()
        
        return {
            'database_uri': db_uri,
            'database_file_path': db_path,
            'file_exists': os.path.exists(db_path) if db_path != 'unknown' else False,
            'working_directory': os.getcwd(),
            'users_count': len(users),
            'users': [{'username': u.username, 'role': u.role} for u in users]
        }
    except Exception as e:
        return {'error': str(e), 'type': type(e).__name__}, 500

@app.route('/health')
def health_check():
    """Detailed health check"""
    try:
        # Test database connection
        db.session.execute(db.text('SELECT 1'))
        db_status = 'connected'
    except Exception as e:
        db_status = f'error: {str(e)}'
    
    try:
        # Test Redis connection
        if redis:
            redis.ping()
            redis_status = 'connected'
        else:
            redis_status = 'not configured'
    except Exception as e:
        redis_status = f'error: {str(e)}'
    
    return {
        'service': 'Vehicle Parking App API',
        'status': 'healthy',
        'database': db_status,
        'redis': redis_status,
        'models': {
            'User': User.__name__,
            'ParkingLot': ParkingLot.__name__,
            'ParkingSpot': ParkingSpot.__name__,
            'Reservation': Reservation.__name__
        }
    }

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5004, debug=True)