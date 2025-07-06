from flask import Flask
from celery import Celery
from backend.models.models import db, User, ParkingLot, ParkingSpot
from backend.routes.auth import auth_bp
from backend.routes.admin import admin_bp
   

celery = Celery(__name__, broker='redis://localhost:6379/0')

def create_app():
    app = Flask(__name__)
    
    app.register_blueprint(admin_bp)
    app.config['SECRET_KEY'] = 'your-secret'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///parking.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
    app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'

    db.init_app(app)
    celery.conf.update(app.config)

    app.register_blueprint(auth_bp)

    with app.app_context():
        db.create_all()

        # ✅ Move this inside app context
        from backend.models.models import User
        from werkzeug.security import generate_password_hash

        if not User.query.filter_by(role='admin').first():
            admin = User(
                username='admin',
                email='admin@system.com',
                password=generate_password_hash('adminpass', method='pbkdf2:sha256'),
                role='admin'
            )
            db.session.add(admin)
            db.session.commit()
            print("✅ Admin user created: admin / adminpass")
            

    return app