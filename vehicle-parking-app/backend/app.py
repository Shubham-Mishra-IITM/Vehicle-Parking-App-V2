from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from redis import Redis
from config import Config
from routes import register_routes

app = Flask(__name__)
app.config.from_object(Config)

# Initialize database
db = SQLAlchemy(app)

# Initialize Redis
redis = Redis(host=Config.REDIS_HOST, port=Config.REDIS_PORT)

# Enable CORS
CORS(app)

# Register routes
register_routes(app)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)