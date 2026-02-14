import re
from datetime import datetime

def validate_usn(usn):
    """Validate USN format (10 characters, alphanumeric)"""
    if not usn or len(usn) != 10:
        return False
    return usn.isalnum()

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_cgpa(cgpa):
    """Validate CGPA is between 0.0 and 10.0"""
    try:
        cgpa_float = float(cgpa)
        return 0.0 <= cgpa_float <= 10.0
    except (TypeError, ValueError):
        return False

def check_job_eligibility(student, job):
    """
    Check if student is eligible for a job
    Returns (is_eligible: bool, reason: str or None)
    """
    # Check CGPA requirement
    if student['cgpa'] < job['eligibility_cgpa']:
        return False, f"CGPA requirement: {job['eligibility_cgpa']}"

    # Check branch eligibility
    eligible_branches = job['eligibility_branches'].split(',')
    if student['branch'] not in eligible_branches:
        return False, "Branch not eligible"

    # Check backlogs
    if student['backlogs'] > job['max_backlogs']:
        return False, f"Max backlogs: {job['max_backlogs']}"

    return True, None

def check_application_exists(conn, student_id, job_id):
    """Check if student has already applied to a job"""
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id FROM job_applications WHERE student_id=? AND job_id=?",
        (student_id, job_id)
    )
    return cursor.fetchone() is not None

def check_job_deadline(last_date_str):
    """Check if job application deadline has passed"""
    try:
        last_date = datetime.strptime(last_date_str, '%Y-%m-%d')
        return datetime.now() <= last_date
    except:
        return False

def dict_from_row(row):
    """Convert sqlite3.Row to dictionary"""
    if row is None:
        return None
    return dict(row)
