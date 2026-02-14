from flask import Blueprint, request, jsonify, session
from database import get_db_connection
from middleware import require_auth, require_student, require_admin
from utils import check_job_eligibility, check_application_exists, check_job_deadline, dict_from_row
from datetime import datetime

jobs_bp = Blueprint('jobs', __name__)

@jobs_bp.route('/', methods=['GET'])
@require_auth
def get_jobs():
    """Get all active job postings (students see eligible jobs)"""
    status_filter = request.args.get('status', 'active')

    conn = get_db_connection()
    cursor = conn.cursor()

    if session['role'] == 'student':
        # Get student details for eligibility check
        cursor.execute("SELECT * FROM users WHERE id=?", (session['user_id'],))
        student = dict_from_row(cursor.fetchone())

        # Get jobs
        cursor.execute("SELECT * FROM jobs WHERE status=? ORDER BY posted_at DESC", (status_filter,))
        jobs = cursor.fetchall()

        # Get student's applications
        cursor.execute("SELECT job_id FROM job_applications WHERE student_id=?", (session['user_id'],))
        applications = [row['job_id'] for row in cursor.fetchall()]

        result = []
        for job in jobs:
            job_dict = dict_from_row(job)
            is_eligible, reason = check_job_eligibility(student, job_dict)
            job_dict['is_eligible'] = is_eligible
            job_dict['has_applied'] = job_dict['id'] in applications
            result.append(job_dict)

        conn.close()
        return jsonify({"success": True, "jobs": result}), 200

    else:  # Admin
        cursor.execute("SELECT * FROM jobs ORDER BY posted_at DESC")
        jobs = cursor.fetchall()
        conn.close()

        return jsonify({"success": True, "jobs": [dict_from_row(j) for j in jobs]}), 200

@jobs_bp.route('/', methods=['POST'])
@require_admin
def create_job():
    """Create new job posting (Admin only)"""
    data = request.get_json()

    required_fields = ['company_name', 'job_title', 'eligibility_cgpa',
                      'eligibility_branches', 'last_date']
    for field in required_fields:
        if field not in data:
            return jsonify({"success": False, "error": f"Missing required field: {field}"}), 400

    # Validate date format
    try:
        datetime.strptime(data['last_date'], '%Y-%m-%d')
    except ValueError:
        return jsonify({"success": False, "error": "Invalid date format for last_date (use YYYY-MM-DD)"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('''
            INSERT INTO jobs (
                company_name, job_title, description, eligibility_cgpa,
                eligibility_branches, max_backlogs, salary_package, job_type,
                last_date, status, posted_by
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'active', ?)
        ''', (
            data['company_name'],
            data['job_title'],
            data.get('description', ''),
            data['eligibility_cgpa'],
            data['eligibility_branches'],
            data.get('max_backlogs', 0),
            data.get('salary_package', ''),
            data.get('job_type', 'full_time'),
            data['last_date'],
            session['user_id']
        ))
        conn.commit()

        job_id = cursor.lastrowid
        cursor.execute("SELECT * FROM jobs WHERE id=?", (job_id,))
        job = cursor.fetchone()
        conn.close()

        return jsonify({
            "success": True,
            "message": "Job posted successfully",
            "job": dict_from_row(job)
        }), 201

    except Exception as e:
        conn.close()
        return jsonify({"success": False, "error": str(e)}), 500

@jobs_bp.route('/<int:job_id>/apply', methods=['POST'])
@require_student
def apply_job(job_id):
    """Student applies for a job"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Get job details
    cursor.execute("SELECT * FROM jobs WHERE id=?", (job_id,))
    job = cursor.fetchone()

    if not job:
        conn.close()
        return jsonify({"success": False, "error": "Job not found"}), 404

    job_dict = dict_from_row(job)

    # Check deadline
    if not check_job_deadline(job_dict['last_date']):
        conn.close()
        return jsonify({"success": False, "error": "Application deadline has passed"}), 400

    # Get student details
    cursor.execute("SELECT * FROM users WHERE id=?", (session['user_id'],))
    student = dict_from_row(cursor.fetchone())

    # Check eligibility
    is_eligible, reason = check_job_eligibility(student, job_dict)
    if not is_eligible:
        conn.close()
        return jsonify({"success": False, "error": f"You are not eligible for this job: {reason}"}), 400

    # Check if already applied
    if check_application_exists(conn, session['user_id'], job_id):
        conn.close()
        return jsonify({"success": False, "error": "Already applied to this job"}), 400

    # Create application
    try:
        cursor.execute('''
            INSERT INTO job_applications (job_id, student_id, status)
            VALUES (?, ?, 'applied')
        ''', (job_id, session['user_id']))
        conn.commit()

        application_id = cursor.lastrowid
        cursor.execute("SELECT * FROM job_applications WHERE id=?", (application_id,))
        application = cursor.fetchone()
        conn.close()

        return jsonify({
            "success": True,
            "message": "Application submitted successfully",
            "application": {
                "id": application['id'],
                "job_id": application['job_id'],
                "status": application['status'],
                "applied_at": application['applied_at']
            }
        }), 201

    except Exception as e:
        conn.close()
        return jsonify({"success": False, "error": str(e)}), 500

@jobs_bp.route('/applications', methods=['GET'])
@require_student
def get_applications():
    """Get student's job applications"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT ja.*, j.company_name, j.job_title, j.salary_package
        FROM job_applications ja
        JOIN jobs j ON ja.job_id = j.id
        WHERE ja.student_id=?
        ORDER BY ja.applied_at DESC
    ''', (session['user_id'],))

    applications = cursor.fetchall()
    conn.close()

    result = []
    for app in applications:
        result.append({
            "id": app['id'],
            "job": {
                "id": app['job_id'],
                "company_name": app['company_name'],
                "job_title": app['job_title'],
                "salary_package": app['salary_package']
            },
            "status": app['status'],
            "applied_at": app['applied_at']
        })

    return jsonify({
        "success": True,
        "applications": result
    }), 200

@jobs_bp.route('/applications/<int:application_id>/status', methods=['PUT'])
@require_admin
def update_application_status(application_id):
    """Update application status (Admin only)"""
    data = request.get_json()

    if 'status' not in data:
        return jsonify({"success": False, "error": "Missing status field"}), 400

    allowed_statuses = ['applied', 'shortlisted', 'rejected', 'selected']
    if data['status'] not in allowed_statuses:
        return jsonify({"success": False, "error": f"Invalid status. Allowed: {', '.join(allowed_statuses)}"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('''
            UPDATE job_applications
            SET status=?, notes=?, updated_at=CURRENT_TIMESTAMP
            WHERE id=?
        ''', (data['status'], data.get('notes', ''), application_id))
        conn.commit()
        conn.close()

        return jsonify({
            "success": True,
            "message": "Application status updated"
        }), 200

    except Exception as e:
        conn.close()
        return jsonify({"success": False, "error": str(e)}), 500
