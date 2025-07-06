from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from backend.models.models import db
from backend.models.models import User
import jwt
import datetime
from flask import current_app

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

# Registration Route
@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.json
    if User.query.filter((User.username == data['username']) | (User.email == data['email'])).first():
        return jsonify({'error': 'User already exists'}), 400

    hashed_password = generate_password_hash(data['password'], method='pbkdf2:sha256')
    user = User(
        username=data['username'],
        email=data['email'],
        password=hashed_password,
        role='user'  # default role
    )
    db.session.add(user)
    db.session.commit()
    return jsonify({'message': 'User registered successfully'}), 201

# Login Route
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(username=data['username']).first()
    if not user or not check_password_hash(user.password, data['password']):
        return jsonify({'error': 'Invalid credentials'}), 401

    token = jwt.encode({
        'user_id': user.id,
        'role': user.role,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    }, current_app.config['SECRET_KEY'], algorithm='HS256')

    return jsonify({'token': token})

from backend.utils.auth import token_required

# Test route - for logged-in users
@auth_bp.route('/user/dashboard', methods=['GET'])
@token_required()  # any authenticated user
def user_dashboard(current_user):
    return jsonify({
        'message': f"Welcome {current_user.username}!",
        'role': current_user.role
    })

# Test route - admin only
@auth_bp.route('/admin/dashboard', methods=['GET'])
@token_required(role='admin')  # only admin
def admin_dashboard(current_user):
    return jsonify({
        'message': f"Hello Admin {current_user.username}",
        'email': current_user.email
    })