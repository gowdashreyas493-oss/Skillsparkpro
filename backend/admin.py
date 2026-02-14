from flask import Blueprint, request, jsonify
from database import get_db_connection
from middleware import require_admin
from utils import dict_from_row

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/students', methods=['GET'])
@require_admin
def get_students():
    """Get all students (Admin only)"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT id, usn, name, email, branch, year, cgpa, backlogs, skills, phone, created_at
        FROM users
        WHERE role='student'
        ORDER BY created_at DESC
    ''')

    students = cursor.fetchall()
    conn.close()

    return jsonify({
        "success": True,
        "students": [dict_from_row(s) for s in students]
    }), 200

@admin_bp.route('/applications', methods=['GET'])
@require_admin
def get_job_applications():
    """Get applications for a specific job (Admin only)"""
    job_id = request.args.get('job_id')

    if not job_id:
        return jsonify({"success": False, "error": "Missing job_id parameter"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT ja.*, u.usn, u.name, u.branch, u.cgpa, u.backlogs
        FROM job_applications ja
        JOIN users u ON ja.student_id = u.id
        WHERE ja.job_id=?
        ORDER BY ja.applied_at DESC
    ''', (job_id,))

    applications = cursor.fetchall()
    conn.close()

    return jsonify({
        "success": True,
        "applications": [dict_from_row(a) for a in applications]
    }), 200

@admin_bp.route('/exams/flagged', methods=['GET'])
@require_admin
def get_flagged_exams():
    """Get exams flagged for review (Admin only)"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT se.*, e.title as exam_title, u.usn, u.name
        FROM student_exams se
        JOIN exams e ON se.exam_id = e.id
        JOIN users u ON se.student_id = u.id
        WHERE se.flagged_for_review=1
        ORDER BY se.end_time DESC
    ''')

    flagged = cursor.fetchall()
    conn.close()

    return jsonify({
        "success": True,
        "flagged_exams": [dict_from_row(f) for f in flagged]
    }), 200

@admin_bp.route('/exams/<int:exam_id>/results', methods=['GET'])
@require_admin
def get_exam_results(exam_id):
    """Get results for all students in an exam (Admin only)"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT se.*, u.usn, u.name, e.total_marks, e.passing_marks
        FROM student_exams se
        JOIN users u ON se.student_id = u.id
        JOIN exams e ON se.exam_id = e.id
        WHERE se.exam_id=? AND se.status IN ('submitted', 'evaluated')
        ORDER BY se.total_score DESC
    ''', (exam_id,))

    results = cursor.fetchall()
    conn.close()

    return jsonify({
        "success": True,
        "results": [dict_from_row(r) for r in results]
    }), 200

@admin_bp.route('/student/<int:student_id>/details', methods=['GET'])
@require_admin
def get_student_details(student_id):
    """Get detailed student information (Admin only)"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Get student info
    cursor.execute("SELECT * FROM users WHERE id=? AND role='student'", (student_id,))
    student = cursor.fetchone()

    if not student:
        conn.close()
        return jsonify({"success": False, "error": "Student not found"}), 404

    # Get enrolled courses
    cursor.execute('''
        SELECT c.title, sc.status, sc.progress_percentage, sc.enrolled_at
        FROM student_courses sc
        JOIN courses c ON sc.course_id = c.id
        WHERE sc.student_id=?
    ''', (student_id,))
    courses = cursor.fetchall()

    # Get job applications
    cursor.execute('''
        SELECT j.company_name, j.job_title, ja.status, ja.applied_at
        FROM job_applications ja
        JOIN jobs j ON ja.job_id = j.id
        WHERE ja.student_id=?
    ''', (student_id,))
    applications = cursor.fetchall()

    # Get exam history
    cursor.execute('''
        SELECT e.title, se.total_score, se.percentage, se.result, se.end_time
        FROM student_exams se
        JOIN exams e ON se.exam_id = e.id
        WHERE se.student_id=? AND se.status='evaluated'
        ORDER BY se.end_time DESC
    ''', (student_id,))
    exams = cursor.fetchall()

    conn.close()

    return jsonify({
        "success": True,
        "student": dict_from_row(student),
        "courses": [dict_from_row(c) for c in courses],
        "applications": [dict_from_row(a) for a in applications],
        "exams": [dict_from_row(e) for e in exams]
    }), 200
