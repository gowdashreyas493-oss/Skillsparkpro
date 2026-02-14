from flask import Blueprint, request, jsonify, session
from database import get_db_connection
from middleware import require_student
from utils import validate_cgpa, dict_from_row

students_bp = Blueprint('students', __name__)

@students_bp.route('/profile', methods=['GET'])
@require_student
def get_profile():
    """Get logged-in student's profile"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE id=?", (session['user_id'],))
    student = cursor.fetchone()
    conn.close()

    if not student:
        return jsonify({"success": False, "error": "Student not found"}), 404

    return jsonify({
        "success": True,
        "student": {
            "id": student['id'],
            "usn": student['usn'],
            "name": student['name'],
            "email": student['email'],
            "branch": student['branch'],
            "year": student['year'],
            "cgpa": student['cgpa'],
            "backlogs": student['backlogs'],
            "skills": student['skills'],
            "phone": student['phone']
        }
    }), 200

@students_bp.route('/profile', methods=['PUT'])
@require_student
def update_profile():
    """Update student's profile"""
    data = request.get_json()

    # Validate CGPA if provided
    if 'cgpa' in data and not validate_cgpa(data['cgpa']):
        return jsonify({"success": False, "error": "Invalid CGPA value"}), 400

    # Validate backlogs if provided
    if 'backlogs' in data:
        try:
            backlogs = int(data['backlogs'])
            if backlogs < 0:
                return jsonify({"success": False, "error": "Backlogs must be non-negative"}), 400
        except (TypeError, ValueError):
            return jsonify({"success": False, "error": "Invalid backlogs value"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    # Build update query dynamically
    update_fields = []
    update_values = []

    allowed_fields = ['name', 'phone', 'skills', 'cgpa', 'backlogs']
    for field in allowed_fields:
        if field in data:
            update_fields.append(f"{field}=?")
            update_values.append(data[field])

    if not update_fields:
        conn.close()
        return jsonify({"success": False, "error": "No fields to update"}), 400

    update_values.append(session['user_id'])
    query = f"UPDATE users SET {', '.join(update_fields)} WHERE id=?"

    try:
        cursor.execute(query, update_values)
        conn.commit()

        # Get updated student
        cursor.execute("SELECT * FROM users WHERE id=?", (session['user_id'],))
        student = cursor.fetchone()
        conn.close()

        return jsonify({
            "success": True,
            "message": "Profile updated successfully",
            "student": {
                "id": student['id'],
                "usn": student['usn'],
                "name": student['name'],
                "email": student['email'],
                "branch": student['branch'],
                "year": student['year'],
                "cgpa": student['cgpa'],
                "backlogs": student['backlogs'],
                "skills": student['skills'],
                "phone": student['phone']
            }
        }), 200

    except Exception as e:
        conn.close()
        return jsonify({"success": False, "error": str(e)}), 500

@students_bp.route('/courses', methods=['GET'])
@require_student
def get_courses():
    """Get all courses with student's enrollment status"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Get all courses
    cursor.execute("SELECT * FROM courses ORDER BY id")
    courses = cursor.fetchall()

    # Get student's enrollments
    cursor.execute('''
        SELECT course_id, status, progress_percentage
        FROM student_courses
        WHERE student_id=?
    ''', (session['user_id'],))
    enrollments = cursor.fetchall()

    # Create enrollment lookup
    enrollment_map = {e['course_id']: e for e in enrollments}

    result = []
    for course in courses:
        course_dict = dict_from_row(course)
        course_id = course['id']

        if course_id in enrollment_map:
            enrollment = enrollment_map[course_id]
            course_dict['enrolled'] = True
            course_dict['status'] = enrollment['status']
            course_dict['progress_percentage'] = enrollment['progress_percentage']
        else:
            course_dict['enrolled'] = False

        result.append(course_dict)

    conn.close()

    return jsonify({
        "success": True,
        "courses": result
    }), 200

@students_bp.route('/courses/<int:course_id>/enroll', methods=['POST'])
@require_student
def enroll_course(course_id):
    """Enroll student in a course"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if course exists
    cursor.execute("SELECT id FROM courses WHERE id=?", (course_id,))
    if not cursor.fetchone():
        conn.close()
        return jsonify({"success": False, "error": "Course not found"}), 404

    # Check if already enrolled
    cursor.execute('''
        SELECT id FROM student_courses
        WHERE student_id=? AND course_id=?
    ''', (session['user_id'], course_id))

    if cursor.fetchone():
        conn.close()
        return jsonify({"success": False, "error": "Already enrolled in this course"}), 400

    # Enroll student
    try:
        cursor.execute('''
            INSERT INTO student_courses (student_id, course_id, status, progress_percentage)
            VALUES (?, ?, 'in_progress', 0)
        ''', (session['user_id'], course_id))
        conn.commit()

        # Get enrollment details
        cursor.execute('''
            SELECT * FROM student_courses
            WHERE student_id=? AND course_id=?
        ''', (session['user_id'], course_id))
        enrollment = cursor.fetchone()

        conn.close()

        return jsonify({
            "success": True,
            "message": "Enrolled successfully",
            "enrollment": {
                "course_id": enrollment['course_id'],
                "status": enrollment['status'],
                "progress_percentage": enrollment['progress_percentage'],
                "enrolled_at": enrollment['enrolled_at']
            }
        }), 201

    except Exception as e:
        conn.close()
        return jsonify({"success": False, "error": str(e)}), 500

@students_bp.route('/courses/<int:course_id>/progress', methods=['PUT'])
@require_student
def update_progress(course_id):
    """Update progress in a course"""
    data = request.get_json()

    if 'progress_percentage' not in data:
        return jsonify({"success": False, "error": "Missing progress_percentage"}), 400

    try:
        progress = int(data['progress_percentage'])
        if not 0 <= progress <= 100:
            return jsonify({"success": False, "error": "Progress must be between 0 and 100"}), 400
    except (TypeError, ValueError):
        return jsonify({"success": False, "error": "Invalid progress value"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if enrolled
    cursor.execute('''
        SELECT id FROM student_courses
        WHERE student_id=? AND course_id=?
    ''', (session['user_id'], course_id))

    if not cursor.fetchone():
        conn.close()
        return jsonify({"success": False, "error": "Not enrolled in this course"}), 400

    # Update progress
    try:
        # If progress is 100, mark as completed
        if progress >= 100:
            cursor.execute('''
                UPDATE student_courses
                SET progress_percentage=100, status='completed', completed_at=CURRENT_TIMESTAMP
                WHERE student_id=? AND course_id=?
            ''', (session['user_id'], course_id))
        else:
            cursor.execute('''
                UPDATE student_courses
                SET progress_percentage=?
                WHERE student_id=? AND course_id=?
            ''', (progress, session['user_id'], course_id))

        conn.commit()
        conn.close()

        return jsonify({
            "success": True,
            "message": "Progress updated"
        }), 200

    except Exception as e:
        conn.close()
        return jsonify({"success": False, "error": str(e)}), 500
