from functools import wraps
from flask import request, jsonify, current_app
from backend.models.models import User
import jwt

def token_required(role=None):
    def wrapper(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            token = None
            if 'Authorization' in request.headers:
                parts = request.headers['Authorization'].split(" ")
                if len(parts) == 2 and parts[0] == "Bearer":
                    token = parts[1]

            if not token:
                return jsonify({'message': 'Token is missing!'}), 401

            try:
                decoded = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
                user = User.query.get(decoded['user_id'])

                if user is None:
                    return jsonify({'message': 'User not found'}), 404

                if role and user.role != role:
                    return jsonify({'message': 'Unauthorized role access'}), 403

            except Exception as e:
                return jsonify({'message': 'Token is invalid', 'error': str(e)}), 401

            return f(user, *args, **kwargs)
        return decorated
    return wrapper