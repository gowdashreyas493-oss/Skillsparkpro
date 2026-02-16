import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'database.db')

def get_db_connection():
    """Returns SQLite connection with row factory for dict-like access"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Enables column access by name
    return conn

def init_database():
    """Creates all tables if they don't exist"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Table 1: users
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usn TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('student', 'admin')),
            branch TEXT,
            year INTEGER,
            cgpa REAL,
            backlogs INTEGER DEFAULT 0,
            skills TEXT,
            phone TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Table 2: courses
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS courses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            category TEXT NOT NULL CHECK(category IN ('programming', 'aptitude')),
            description TEXT,
            content TEXT,
            duration_hours INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Table 3: student_courses
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS student_courses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            course_id INTEGER NOT NULL,
            status TEXT DEFAULT 'in_progress' CHECK(status IN ('in_progress', 'completed')),
            progress_percentage INTEGER DEFAULT 0,
            enrolled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES users(id),
            FOREIGN KEY (course_id) REFERENCES courses(id),
            UNIQUE(student_id, course_id)
        )
    ''')

    # Table 4: jobs
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_name TEXT NOT NULL,
            job_title TEXT NOT NULL,
            description TEXT,
            eligibility_cgpa REAL NOT NULL,
            eligibility_branches TEXT NOT NULL,
            max_backlogs INTEGER DEFAULT 0,
            salary_package TEXT,
            job_type TEXT CHECK(job_type IN ('full_time', 'internship')),
            last_date DATE NOT NULL,
            status TEXT DEFAULT 'active' CHECK(status IN ('active', 'closed')),
            posted_by INTEGER,
            posted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (posted_by) REFERENCES users(id)
        )
    ''')

    # Table 5: job_applications
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS job_applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_id INTEGER NOT NULL,
            student_id INTEGER NOT NULL,
            status TEXT DEFAULT 'applied' CHECK(status IN ('applied', 'shortlisted', 'rejected', 'selected')),
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            notes TEXT,
            FOREIGN KEY (job_id) REFERENCES jobs(id),
            FOREIGN KEY (student_id) REFERENCES users(id),
            UNIQUE(job_id, student_id)
        )
    ''')

    # Table 6: exams
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS exams (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            course_id INTEGER,
            exam_type TEXT NOT NULL CHECK(exam_type IN ('mcq', 'coding', 'mixed')),
            duration_minutes INTEGER NOT NULL,
            total_marks INTEGER NOT NULL,
            passing_marks INTEGER NOT NULL,
            instructions TEXT,
            scheduled_date TIMESTAMP,
            status TEXT DEFAULT 'draft' CHECK(status IN ('draft', 'published', 'completed')),
            proctoring_enabled INTEGER DEFAULT 1,
            created_by INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (course_id) REFERENCES courses(id),
            FOREIGN KEY (created_by) REFERENCES users(id)
        )
    ''')

    # Table 7: questions
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            exam_id INTEGER NOT NULL,
            question_type TEXT NOT NULL CHECK(question_type IN ('mcq', 'coding')),
            question_text TEXT NOT NULL,
            option_a TEXT,
            option_b TEXT,
            option_c TEXT,
            option_d TEXT,
            correct_answer TEXT,
            marks INTEGER NOT NULL,
            difficulty TEXT CHECK(difficulty IN ('easy', 'medium', 'hard')),
            language TEXT,
            test_cases TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (exam_id) REFERENCES exams(id)
        )
    ''')

    # Table 8: student_exams
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS student_exams (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            exam_id INTEGER NOT NULL,
            student_id INTEGER NOT NULL,
            status TEXT DEFAULT 'not_started' CHECK(status IN ('not_started', 'in_progress', 'submitted', 'evaluated')),
            start_time TIMESTAMP,
            end_time TIMESTAMP,
            time_taken_minutes INTEGER,
            mcq_score INTEGER DEFAULT 0,
            coding_score INTEGER DEFAULT 0,
            total_score INTEGER DEFAULT 0,
            percentage REAL DEFAULT 0.0,
            result TEXT CHECK(result IN ('pass', 'fail', 'pending_evaluation')),
            violation_count INTEGER DEFAULT 0,
            flagged_for_review INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (exam_id) REFERENCES exams(id),
            FOREIGN KEY (student_id) REFERENCES users(id)
        )
    ''')

    # Table 9: student_answers
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS student_answers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_exam_id INTEGER NOT NULL,
            question_id INTEGER NOT NULL,
            answer_type TEXT CHECK(answer_type IN ('mcq_option', 'code')),
            answer_value TEXT,
            is_correct INTEGER,
            marks_awarded INTEGER DEFAULT 0,
            evaluated_by INTEGER,
            evaluated_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_exam_id) REFERENCES student_exams(id),
            FOREIGN KEY (question_id) REFERENCES questions(id),
            FOREIGN KEY (evaluated_by) REFERENCES users(id)
        )
    ''')

    # Table 10: proctoring_logs
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS proctoring_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_exam_id INTEGER NOT NULL,
            violation_type TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            severity TEXT CHECK(severity IN ('low', 'medium', 'high')),
            details TEXT,
            image_path TEXT,
            FOREIGN KEY (student_exam_id) REFERENCES student_exams(id)
        )
    ''')

    # Table 11: analytics
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS analytics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            metric_type TEXT NOT NULL,
            metric_value TEXT,
            calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES users(id)
        )
    ''')

    conn.commit()
    conn.close()
    print("Database initialized successfully with all 11 tables.")

if __name__ == '__main__':
    init_database()
