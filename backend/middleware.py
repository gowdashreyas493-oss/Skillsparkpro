from functools import wraps
from flask import session, jsonify

def require_auth(f):
    """Decorator to require authentication for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({
                "authenticated": False,
                "message": "Authentication required"
            }), 401
        return f(*args, **kwargs)
    return decorated_function

def require_student(f):
    """Decorator to require student role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({
                "authenticated": False,
                "message": "Authentication required"
            }), 401
        if session.get('role') != 'student':
            return jsonify({
                "error": "Student access only"
            }), 403
        return f(*args, **kwargs)
    return decorated_function

def require_admin(f):
    """Decorator to require admin role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({
                "authenticated": False,
                "message": "Authentication required"
            }), 401
        if session.get('role') != 'admin':
            return jsonify({
                "error": "Admin access only"
            }), 403
        return f(*args, **kwargs)
    return decorated_function

def get_current_user():
    """Get current user information from session"""
    if 'user_id' in session:
        return {
            'id': session['user_id'],
            'role': session['role'],
            'usn': session.get('usn'),
            'name': session.get('name')
        }
    return None
