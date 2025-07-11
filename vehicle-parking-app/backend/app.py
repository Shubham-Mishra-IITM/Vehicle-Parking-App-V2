from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from redis import Redis
from config import Config

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Initialize database
db = SQLAlchemy(app)

# Update the db instance in all models
import models.user as user_module
import models.parking_lot as parking_lot_module
import models.parking_spot as parking_spot_module
import models.reservation as reservation_module

user_module.db = db
parking_lot_module.db = db
parking_spot_module.db = db
reservation_module.db = db

# Now import models for database operations
from models import User, ParkingLot, ParkingSpot, Reservation

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

@app.route('/health')
def health_check():
    """Detailed health check"""
    try:
        # Test database connection
        db.session.execute('SELECT 1')
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
    app.run(host='0.0.0.0', port=5000, debug=True)