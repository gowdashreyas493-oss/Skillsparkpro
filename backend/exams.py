from flask import Blueprint, request, jsonify, session
from database import get_db_connection
from middleware import require_auth, require_student, require_admin
from utils import dict_from_row
from datetime import datetime, timedelta
import json

exams_bp = Blueprint('exams', __name__)

@exams_bp.route('/', methods=['GET'])
@require_auth
def get_exams():
    """Get all exams (students see published exams, admins see all)"""
    conn = get_db_connection()
    cursor = conn.cursor()

    if session['role'] == 'student':
        # Get published exams
        cursor.execute('''
            SELECT e.* FROM exams e
            WHERE e.status='published'
            ORDER BY e.scheduled_date ASC
        ''')
        exams = cursor.fetchall()

        result = []
        for exam in exams:
            exam_dict = dict_from_row(exam)

            # Check student's attempt status
            cursor.execute('''
                SELECT status FROM student_exams
                WHERE exam_id=? AND student_id=?
                ORDER BY created_at DESC LIMIT 1
            ''', (exam['id'], session['user_id']))

            attempt = cursor.fetchone()
            exam_dict['attempt_status'] = attempt['status'] if attempt else 'not_started'

            result.append(exam_dict)

        conn.close()
        return jsonify({"success": True, "exams": result}), 200

    else:  # Admin
        cursor.execute("SELECT * FROM exams ORDER BY created_at DESC")
        exams = cursor.fetchall()
        conn.close()

        return jsonify({"success": True, "exams": [dict_from_row(e) for e in exams]}), 200

@exams_bp.route('/', methods=['POST'])
@require_admin
def create_exam():
    """Create new exam (Admin only)"""
    data = request.get_json()

    required_fields = ['title', 'exam_type', 'duration_minutes', 'total_marks', 'passing_marks']
    for field in required_fields:
        if field not in data:
            return jsonify({"success": False, "error": f"Missing required field: {field}"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('''
            INSERT INTO exams (
                title, course_id, exam_type, duration_minutes, total_marks,
                passing_marks, instructions, scheduled_date, status,
                proctoring_enabled, created_by
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'draft', ?, ?)
        ''', (
            data['title'],
            data.get('course_id'),
            data['exam_type'],
            data['duration_minutes'],
            data['total_marks'],
            data['passing_marks'],
            data.get('instructions', ''),
            data.get('scheduled_date'),
            data.get('proctoring_enabled', 1),
            session['user_id']
        ))
        conn.commit()

        exam_id = cursor.lastrowid
        cursor.execute("SELECT * FROM exams WHERE id=?", (exam_id,))
        exam = cursor.fetchone()
        conn.close()

        return jsonify({
            "success": True,
            "message": "Exam created successfully",
            "exam": dict_from_row(exam)
        }), 201

    except Exception as e:
        conn.close()
        return jsonify({"success": False, "error": str(e)}), 500

@exams_bp.route('/<int:exam_id>/questions', methods=['POST'])
@require_admin
def add_question(exam_id):
    """Add question to exam (Admin only)"""
    data = request.get_json()

    if 'question_type' not in data or 'question_text' not in data or 'marks' not in data:
        return jsonify({"success": False, "error": "Missing required fields"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if exam exists
    cursor.execute("SELECT id FROM exams WHERE id=?", (exam_id,))
    if not cursor.fetchone():
        conn.close()
        return jsonify({"success": False, "error": "Exam not found"}), 404

    try:
        if data['question_type'] == 'mcq':
            cursor.execute('''
                INSERT INTO questions (
                    exam_id, question_type, question_text, option_a, option_b,
                    option_c, option_d, correct_answer, marks, difficulty
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                exam_id,
                'mcq',
                data['question_text'],
                data.get('option_a'),
                data.get('option_b'),
                data.get('option_c'),
                data.get('option_d'),
                data.get('correct_answer'),
                data['marks'],
                data.get('difficulty', 'medium')
            ))
        else:  # coding
            test_cases_json = json.dumps(data.get('test_cases', []))
            cursor.execute('''
                INSERT INTO questions (
                    exam_id, question_type, question_text, marks, difficulty,
                    language, test_cases
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                exam_id,
                'coding',
                data['question_text'],
                data['marks'],
                data.get('difficulty', 'medium'),
                data.get('language', 'python'),
                test_cases_json
            ))

        conn.commit()
        question_id = cursor.lastrowid
        cursor.execute("SELECT * FROM questions WHERE id=?", (question_id,))
        question = cursor.fetchone()
        conn.close()

        return jsonify({
            "success": True,
            "message": "Question added successfully",
            "question": dict_from_row(question)
        }), 201

    except Exception as e:
        conn.close()
        return jsonify({"success": False, "error": str(e)}), 500

@exams_bp.route('/<int:exam_id>/publish', methods=['PUT'])
@require_admin
def publish_exam(exam_id):
    """Publish exam to make it visible to students"""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("UPDATE exams SET status='published' WHERE id=?", (exam_id,))
        conn.commit()
        conn.close()

        return jsonify({
            "success": True,
            "message": "Exam published successfully"
        }), 200

    except Exception as e:
        conn.close()
        return jsonify({"success": False, "error": str(e)}), 500

@exams_bp.route('/<int:exam_id>/start', methods=['POST'])
@require_student
def start_exam(exam_id):
    """Start exam for student"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Get exam details
    cursor.execute("SELECT * FROM exams WHERE id=?", (exam_id,))
    exam = cursor.fetchone()

    if not exam:
        conn.close()
        return jsonify({"success": False, "error": "Exam not found"}), 404

    if exam['status'] != 'published':
        conn.close()
        return jsonify({"success": False, "error": "Exam not published yet"}), 400

    # Check if already started
    cursor.execute('''
        SELECT id, status FROM student_exams
        WHERE exam_id=? AND student_id=? AND status='in_progress'
    ''', (exam_id, session['user_id']))

    existing_attempt = cursor.fetchone()
    if existing_attempt:
        conn.close()
        return jsonify({"success": False, "error": "Exam already started"}), 400

    # Create student exam entry
    start_time = datetime.now()
    end_time = start_time + timedelta(minutes=exam['duration_minutes'])

    try:
        cursor.execute('''
            INSERT INTO student_exams (exam_id, student_id, status, start_time)
            VALUES (?, ?, 'in_progress', ?)
        ''', (exam_id, session['user_id'], start_time))
        conn.commit()

        student_exam_id = cursor.lastrowid

        # Get questions (without correct answers)
        cursor.execute('''
            SELECT id, question_type, question_text, option_a, option_b,
                   option_c, option_d, marks, language
            FROM questions
            WHERE exam_id=?
        ''', (exam_id,))
        questions = cursor.fetchall()

        conn.close()

        return jsonify({
            "success": True,
            "message": "Exam started",
            "student_exam_id": student_exam_id,
            "exam": {
                "id": exam['id'],
                "title": exam['title'],
                "duration_minutes": exam['duration_minutes'],
                "total_marks": exam['total_marks'],
                "instructions": exam['instructions'],
                "proctoring_enabled": exam['proctoring_enabled'],
                "questions": [dict_from_row(q) for q in questions]
            },
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat()
        }), 200

    except Exception as e:
        conn.close()
        return jsonify({"success": False, "error": str(e)}), 500

@exams_bp.route('/<int:exam_id>/submit', methods=['POST'])
@require_student
def submit_exam(exam_id):
    """Submit exam answers"""
    data = request.get_json()

    if 'student_exam_id' not in data or 'answers' not in data:
        return jsonify({"success": False, "error": "Missing required fields"}), 400

    student_exam_id = data['student_exam_id']
    answers = data['answers']

    conn = get_db_connection()
    cursor = conn.cursor()

    # Validate student_exam belongs to user
    cursor.execute('''
        SELECT * FROM student_exams
        WHERE id=? AND student_id=?
    ''', (student_exam_id, session['user_id']))

    student_exam = cursor.fetchone()
    if not student_exam:
        conn.close()
        return jsonify({"success": False, "error": "Student exam not found"}), 404

    if student_exam['status'] == 'submitted':
        conn.close()
        return jsonify({"success": False, "error": "Exam already submitted"}), 400

    # Get exam and questions
    cursor.execute("SELECT * FROM exams WHERE id=?", (exam_id,))
    exam = cursor.fetchone()

    cursor.execute("SELECT * FROM questions WHERE exam_id=?", (exam_id,))
    questions = {q['id']: dict_from_row(q) for q in cursor.fetchall()}

    # Process answers
    mcq_score = 0
    coding_score = 0
    has_coding = False

    try:
        for answer in answers:
            question_id = answer['question_id']
            question = questions.get(question_id)

            if not question:
                continue

            is_correct = 0
            marks_awarded = 0

            # Auto-grade MCQ
            if question['question_type'] == 'mcq':
                if answer['answer_value'] == question['correct_answer']:
                    is_correct = 1
                    marks_awarded = question['marks']
                    mcq_score += marks_awarded

            # Coding questions - set for manual evaluation
            else:
                has_coding = True
                # Will be evaluated manually or auto-evaluated later
                is_correct = 0
                marks_awarded = 0

            # Save answer
            cursor.execute('''
                INSERT INTO student_answers (
                    student_exam_id, question_id, answer_type, answer_value,
                    is_correct, marks_awarded
                ) VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                student_exam_id,
                question_id,
                answer['answer_type'],
                answer['answer_value'],
                is_correct,
                marks_awarded
            ))

        # Update student_exam
        end_time = datetime.now()
        start_time = datetime.fromisoformat(student_exam['start_time'])
        time_taken = int((end_time - start_time).total_seconds() / 60)

        total_score = mcq_score + coding_score
        percentage = (total_score / exam['total_marks']) * 100 if exam['total_marks'] > 0 else 0

        # Determine result
        if has_coding:
            result = 'pending_evaluation'
            status = 'submitted'
        else:
            result = 'pass' if total_score >= exam['passing_marks'] else 'fail'
            status = 'evaluated'

        cursor.execute('''
            UPDATE student_exams
            SET status=?, end_time=?, time_taken_minutes=?, mcq_score=?,
                coding_score=?, total_score=?, percentage=?, result=?
            WHERE id=?
        ''', (status, end_time, time_taken, mcq_score, coding_score,
              total_score, percentage, result, student_exam_id))

        conn.commit()
        conn.close()

        return jsonify({
            "success": True,
            "message": "Exam submitted successfully",
            "result": {
                "mcq_score": mcq_score,
                "coding_score": coding_score,
                "total_score": total_score,
                "percentage": percentage,
                "result": result,
                "message": "MCQ results available. Coding questions under evaluation." if has_coding else "Results available."
            }
        }), 200

    except Exception as e:
        conn.close()
        return jsonify({"success": False, "error": str(e)}), 500

@exams_bp.route('/<int:exam_id>/results', methods=['GET'])
@require_student
def get_results(exam_id):
    """Get student's exam result"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT se.*, e.title as exam_title, e.total_marks
        FROM student_exams se
        JOIN exams e ON se.exam_id = e.id
        WHERE se.exam_id=? AND se.student_id=?
        ORDER BY se.created_at DESC LIMIT 1
    ''', (exam_id, session['user_id']))

    result = cursor.fetchone()
    conn.close()

    if not result:
        return jsonify({"success": False, "error": "Exam not attempted"}), 404

    if result['status'] in ['not_started', 'in_progress']:
        return jsonify({
            "success": True,
            "message": "Exam not yet submitted",
            "result": {"status": result['status']}
        }), 200

    if result['result'] == 'pending_evaluation':
        return jsonify({
            "success": True,
            "message": "Evaluation in progress",
            "result": {
                "status": "pending_evaluation",
                "mcq_score": result['mcq_score'],
                "coding_score": result['coding_score']
            }
        }), 200

    return jsonify({
        "success": True,
        "result": {
            "exam_title": result['exam_title'],
            "total_marks": result['total_marks'],
            "mcq_score": result['mcq_score'],
            "coding_score": result['coding_score'],
            "total_score": result['total_score'],
            "percentage": result['percentage'],
            "result": result['result'],
            "time_taken_minutes": result['time_taken_minutes'],
            "violation_count": result['violation_count'],
            "submitted_at": result['end_time']
        }
    }), 200

@exams_bp.route('/answers/<int:answer_id>/evaluate', methods=['PUT'])
@require_admin
def evaluate_answer(answer_id):
    """Manually evaluate coding answer (Admin only)"""
    data = request.get_json()

    if 'marks_awarded' not in data or 'is_correct' not in data:
        return jsonify({"success": False, "error": "Missing required fields"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Update answer
        cursor.execute('''
            UPDATE student_answers
            SET marks_awarded=?, is_correct=?, evaluated_by=?, evaluated_at=CURRENT_TIMESTAMP
            WHERE id=?
        ''', (data['marks_awarded'], data['is_correct'], session['user_id'], answer_id))

        # Get student_exam_id to recalculate scores
        cursor.execute("SELECT student_exam_id FROM student_answers WHERE id=?", (answer_id,))
        student_exam_id = cursor.fetchone()['student_exam_id']

        # Recalculate coding score
        cursor.execute('''
            SELECT SUM(marks_awarded) as total FROM student_answers
            WHERE student_exam_id=? AND answer_type='code'
        ''', (student_exam_id,))
        coding_score = cursor.fetchone()['total'] or 0

        # Get MCQ score and exam details
        cursor.execute('''
            SELECT se.mcq_score, e.total_marks, e.passing_marks
            FROM student_exams se
            JOIN exams e ON se.exam_id = e.id
            WHERE se.id=?
        ''', (student_exam_id,))
        exam_data = cursor.fetchone()

        total_score = exam_data['mcq_score'] + coding_score
        percentage = (total_score / exam_data['total_marks']) * 100
        result = 'pass' if total_score >= exam_data['passing_marks'] else 'fail'

        # Update student_exam
        cursor.execute('''
            UPDATE student_exams
            SET coding_score=?, total_score=?, percentage=?, result=?, status='evaluated'
            WHERE id=?
        ''', (coding_score, total_score, percentage, result, student_exam_id))

        conn.commit()
        conn.close()

        return jsonify({
            "success": True,
            "message": "Answer evaluated successfully"
        }), 200

    except Exception as e:
        conn.close()
        return jsonify({"success": False, "error": str(e)}), 500
