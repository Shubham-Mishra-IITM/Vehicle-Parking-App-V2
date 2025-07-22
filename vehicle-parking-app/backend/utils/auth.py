from functools import wraps
from flask import request, jsonify, current_app
import jwt

def token_required(f):
    """Decorator to require valid authentication token"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        try:
            if token.startswith('Bearer '):
                token = token[7:]
            
            payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            request.current_user_id = payload['user_id']
            request.current_user_role = payload['role']
            
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
        except Exception as e:
            return jsonify({'error': str(e)}), 500
            
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Decorator to require admin authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        try:
            if token.startswith('Bearer '):
                token = token[7:]
            
            payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            
            if payload.get('role') != 'admin':
                return jsonify({'error': 'Admin access required'}), 403
                
            request.current_user_id = payload['user_id']
            request.current_user_role = payload['role']
            
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
        except Exception as e:
            return jsonify({'error': str(e)}), 500
            
        return f(*args, **kwargs)
    return decorated_function

def user_required(f):
    """Decorator to require user authentication (non-admin)"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        try:
            if token.startswith('Bearer '):
                token = token[7:]
            
            payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            
            if payload.get('role') != 'user':
                return jsonify({'error': 'User access required'}), 403
                
            request.current_user_id = payload['user_id']
            request.current_user_role = payload['role']
            
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
        except Exception as e:
            return jsonify({'error': str(e)}), 500
            
        return f(*args, **kwargs)
    return decorated_function

def get_current_user_from_token():
    """Extract current user info from token"""
    token = request.headers.get('Authorization')
    if not token:
        return None
    
    try:
        if token.startswith('Bearer '):
            token = token[7:]
        
        payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        return {
            'user_id': payload['user_id'],
            'role': payload['role']
        }
    except:
        return None
