# SkillSpark Pro

Placement, Training & Secure Online Assessment System with AI-Powered Proctoring

## Overview

SkillSpark Pro is a comprehensive web application designed to help colleges manage:
- **Student Training**: Course enrollment with progress tracking
- **Placement Management**: Job postings with eligibility-based applications
- **Secure Assessments**: Online exams with AI proctoring capabilities

## Features

### For Students
- Register and manage profile (USN, CGPA, skills)
- Browse and enroll in courses (Python, Java, C/C++, Aptitude, etc.)
- Apply to job postings based on eligibility
- Take proctored online exams (MCQ and coding questions)
- View results and track performance

### For Admins/TPO
- Manage students and view profiles
- Post job openings with eligibility criteria
- Create exams with MCQ and coding questions
- Review proctoring violations with captured frames
- Evaluate coding submissions and manage applications

### AI Proctoring Features
- **Fullscreen enforcement** with exit detection
- **Tab switch monitoring** and violation logging
- **Facial recognition** (face count detection)
- **Eye tracking** (gaze direction monitoring)
- **Object detection** (mobile phones, books)
- **Auto-submit** after 5 violations

## Technology Stack

- **Backend**: Python Flask 2.3.0, SQLite
- **Frontend**: Vanilla HTML5, CSS3, JavaScript ES6
- **AI/ML**: OpenCV (face detection), MediaPipe (eye tracking), YOLO (object detection)
- **Code Editor**: CodeMirror
- **Authentication**: Session-based with secure cookies

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Modern web browser (Chrome, Firefox, Edge)
- Webcam (for proctored exams)

## Setup Instructions

### 1. Clone the Repository

```bash
git clone <repository-url>
cd Skillsparkpro
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

```bash
# Copy example file
cp .env.example .env

# Generate secret key
python -c "import secrets; print(secrets.token_hex(32))"

# Edit .env and paste the generated key as SECRET_KEY
```

### 5. Initialize Database

```bash
python backend/database.py
```

This creates `backend/database.db` with all required tables.

### 6. Seed Initial Data

```bash
# Create default admin account
python backend/seed_admin.py

# Insert pre-defined courses
python backend/seed_courses.py
```

### 7. Create Required Directories

```bash
mkdir -p backend/proctoring_images
```

### 8. Run the Application

```bash
# Start Flask backend
python backend/app.py
```

Backend runs on: http://localhost:5000

### 9. Access Frontend

Open `frontend/index.html` in your web browser OR use VS Code Live Server extension.

## Default Login Credentials

### Admin Account
- **USN**: ADMIN001
- **Password**: admin123

**Important**: Change the admin password after first login.

## Usage

### Student Workflow
1. Register with university USN
2. Login and complete profile
3. Browse and enroll in courses
4. Apply to eligible job postings
5. Take proctored exams
6. View results and track progress

### Admin Workflow
1. Login with admin credentials
2. Create job postings with eligibility criteria
3. Create exams with MCQ and coding questions
4. Publish exams to students
5. Review applications and shortlist candidates
6. Evaluate coding submissions
7. Review proctoring violations

## API Endpoints

Base URL: http://localhost:5000/api

### Authentication
- `POST /api/auth/register` - Register new student
- `POST /api/auth/login` - User login
- `POST /api/auth/logout` - User logout
- `GET /api/auth/session` - Check session status

### Student
- `GET /api/student/profile` - Get student profile
- `PUT /api/student/profile` - Update profile
- `GET /api/student/courses` - Get courses with enrollment
- `POST /api/student/courses/{id}/enroll` - Enroll in course
- `PUT /api/student/courses/{id}/progress` - Update progress

### Jobs
- `GET /api/jobs` - List job postings
- `POST /api/jobs` - Create job (admin only)
- `POST /api/jobs/{id}/apply` - Apply to job
- `GET /api/jobs/applications` - Get student's applications
- `PUT /api/jobs/applications/{id}/status` - Update application (admin only)

### Exams
- `GET /api/exams` - List exams
- `POST /api/exams` - Create exam (admin only)
- `POST /api/exams/{id}/questions` - Add question (admin only)
- `POST /api/exams/{id}/start` - Start exam
- `POST /api/exams/{id}/submit` - Submit exam
- `GET /api/exams/{id}/results` - Get results
- `PUT /api/exams/answers/{id}/evaluate` - Evaluate answer (admin only)

### Proctoring
- `POST /api/proctoring/violation` - Log violation
- `POST /api/proctoring/frame` - Upload webcam frame
- `GET /api/proctoring/logs/{id}` - Get proctoring logs (admin only)

## Database Schema

The application uses SQLite with 11 tables:
- `users` - Student and admin accounts
- `courses` - Course catalog
- `student_courses` - Enrollment tracking
- `jobs` - Job postings
- `job_applications` - Application management
- `exams` - Exam definitions
- `questions` - Exam questions
- `student_exams` - Exam attempts
- `student_answers` - Student responses
- `proctoring_logs` - Violation records
- `analytics` - Performance metrics

## Security Features

- Password hashing with werkzeug (pbkdf2:sha256)
- Session-based authentication with HttpOnly cookies
- SQL injection prevention with parameterized queries
- XSS protection with content escaping
- Code execution in isolated subprocess with timeout
- CSRF protection with SameSite cookies

## Troubleshooting

### Database Issues
```bash
# Reset database
rm backend/database.db
python backend/database.py
python backend/seed_admin.py
python backend/seed_courses.py
```

### Camera Permission Denied
- Check browser settings to allow camera access
- Exam will continue but be flagged for review

### YOLO Model Download
- First run downloads ~40MB model automatically
- If download fails, object detection is skipped gracefully

### Port Already in Use
```bash
# Change port in backend/app.py
app.run(debug=True, port=5001)
```

## Development

### File Structure
```
Skillsparkpro/
├── backend/          # Flask application
├── frontend/         # HTML/CSS/JS files
├── requirements.txt  # Python dependencies
├── .env             # Environment configuration
└── README.md        # This file
```

### Adding New Features
1. Backend: Add routes in appropriate module (auth.py, students.py, etc.)
2. Frontend: Create HTML page and JS logic
3. Database: Update schema in database.py if needed
4. Test: Verify complete workflow

## License

MIT License - See LICENSE file for details

## Support

For issues or questions:
1. Check troubleshooting section
2. Review API documentation
3. Check browser console for errors
4. Verify backend logs

## Contributors

Copyright 2025 SHREYAS GOWDA G
