from flask import Blueprint, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
from database import get_db_connection
from utils import validate_usn, validate_email, validate_cgpa, dict_from_row

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new student account"""
    data = request.get_json()

    # Validate required fields
    required_fields = ['usn', 'name', 'email', 'password', 'branch', 'year', 'cgpa', 'phone']
    for field in required_fields:
        if field not in data:
            return jsonify({"success": False, "error": f"Missing required field: {field}"}), 400

    # Validate USN
    if not validate_usn(data['usn']):
        return jsonify({"success": False, "error": "Invalid USN format (must be 10 alphanumeric characters)"}), 400

    # Validate email
    if not validate_email(data['email']):
        return jsonify({"success": False, "error": "Invalid email format"}), 400

    # Validate password length
    if len(data['password']) < 6:
        return jsonify({"success": False, "error": "Password must be at least 6 characters"}), 400

    # Validate CGPA
    if not validate_cgpa(data['cgpa']):
        return jsonify({"success": False, "error": "Invalid CGPA value (must be between 0.0 and 10.0)"}), 400

    # Validate year
    if data['year'] not in [1, 2, 3, 4]:
        return jsonify({"success": False, "error": "Year must be 1, 2, 3, or 4"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if first user (for admin flag support)
    cursor.execute("SELECT COUNT(*) as count FROM users WHERE role='admin'")
    admin_count = cursor.fetchone()['count']

    # Determine role
    role = 'student'
    if admin_count == 0 and data.get('is_admin') == True:
        role = 'admin'

    # Check if USN already exists
    cursor.execute("SELECT id FROM users WHERE usn=?", (data['usn'],))
    if cursor.fetchone():
        conn.close()
        return jsonify({"success": False, "error": "USN already exists"}), 400

    # Check if email already exists
    cursor.execute("SELECT id FROM users WHERE email=?", (data['email'],))
    if cursor.fetchone():
        conn.close()
        return jsonify({"success": False, "error": "Email already exists"}), 400

    # Hash password
    hashed_password = generate_password_hash(data['password'], method='pbkdf2:sha256')

    # Insert new user
    try:
        cursor.execute('''
            INSERT INTO users (usn, name, email, password, role, branch, year, cgpa, backlogs, skills, phone)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['usn'],
            data['name'],
            data['email'],
            hashed_password,
            role,
            data['branch'],
            data['year'],
            data['cgpa'],
            data.get('backlogs', 0),
            data.get('skills', ''),
            data['phone']
        ))
        conn.commit()

        user_id = cursor.lastrowid

        # Get created user
        cursor.execute("SELECT * FROM users WHERE id=?", (user_id,))
        user = dict_from_row(cursor.fetchone())

        conn.close()

        # Create session
        session['user_id'] = user['id']
        session['role'] = user['role']
        session['usn'] = user['usn']
        session['name'] = user['name']

        return jsonify({
            "success": True,
            "message": "Registration successful",
            "user": {
                "id": user['id'],
                "usn": user['usn'],
                "name": user['name'],
                "email": user['email'],
                "role": user['role']
            }
        }), 201

    except Exception as e:
        conn.close()
        return jsonify({"success": False, "error": str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """Authenticate user and create session"""
    data = request.get_json()

    if 'usn' not in data or 'password' not in data:
        return jsonify({"success": False, "error": "Missing USN or password"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    # Find user by USN
    cursor.execute("SELECT * FROM users WHERE usn=?", (data['usn'],))
    user = cursor.fetchone()
    conn.close()

    if not user:
        return jsonify({"success": False, "error": "Invalid credentials"}), 401

    # Check password
    if not check_password_hash(user['password'], data['password']):
        return jsonify({"success": False, "error": "Invalid credentials"}), 401

    # Create session
    session['user_id'] = user['id']
    session['role'] = user['role']
    session['usn'] = user['usn']
    session['name'] = user['name']

    return jsonify({
        "success": True,
        "message": "Login successful",
        "user": {
            "id": user['id'],
            "usn": user['usn'],
            "name": user['name'],
            "role": user['role'],
            "branch": user['branch'],
            "cgpa": user['cgpa']
        }
    }), 200

@auth_bp.route('/logout', methods=['POST'])
def logout():
    """Destroy current session"""
    session.clear()
    return jsonify({
        "success": True,
        "message": "Logged out successfully"
    }), 200

@auth_bp.route('/session', methods=['GET'])
def check_session():
    """Check if user has valid session and get user details"""
    if 'user_id' in session:
        return jsonify({
            "authenticated": True,
            "user": {
                "id": session['user_id'],
                "usn": session.get('usn'),
                "name": session.get('name'),
                "role": session.get('role')
            }
        }), 200
    else:
        return jsonify({
            "authenticated": False,
            "message": "No active session"
        }), 401
