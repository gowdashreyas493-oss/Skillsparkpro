# SkillSpark Pro - Complete Setup & Deployment Guide

## Current Implementation Status

### ✅ Completed Components (Backend - 100%)

All backend API modules are fully implemented:

1. **Core Infrastructure**
   - ✅ Database schema (11 tables)
   - ✅ Configuration management
   - ✅ Authentication middleware
   - ✅ Utility functions
   - ✅ Seed scripts

2. **API Endpoints**
   - ✅ Authentication (register, login, logout, session)
   - ✅ Student management (profile, courses, enrollment)
   - ✅ Job management (create, apply, applications)
   - ✅ Exam management (create, start, submit, evaluate)
   - ✅ AI Proctoring (violation logging, frame analysis)
   - ✅ Admin operations (students list, flagged exams, results)

3. **AI Capabilities**
   - ✅ Face detection (OpenCV)
   - ✅ Eye tracking (MediaPipe)
   - ✅ Object detection (YOLO)
   - ✅ Automatic violation logging
   - ✅ Auto-submit on threshold

### ⏳ Remaining Components (Frontend - 30%)

1. **JavaScript Modules** - Partially complete
   - ✅ common.js (API wrapper, utilities)
   - ⏳ auth.js (needed for login)
   - ⏳ student.js, admin.js, exam.js, proctoring.js
   - ⏳ course.js

2. **HTML Pages** - Not started (17 files needed)
   - ⏳ index.html (login/registration)
   - ⏳ 8 student pages
   - ⏳ 7 admin pages
   - ⏳ styles.css

3. **Course Content** - Not started (36 files)
   - ⏳ 6 course folders with learning materials

## Quick Setup Instructions

### 1. Environment Setup

```bash
# Navigate to project directory
cd Skillsparkpro

# Create and activate virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate

# Install all dependencies
pip install -r requirements.txt

# Install additional required packages
pip install python-dotenv flask-session
```

### 2. Environment Configuration

Create `.env` file in project root:

```bash
# Generate secret key
python -c "import secrets; print(secrets.token_hex(32))"

# Copy output and create .env file
```

`.env` content:
```
SECRET_KEY=<paste-generated-key-here>
FLASK_ENV=development
AI_PROCTORING_ENABLED=True
FRAME_CAPTURE_INTERVAL=10
AUTO_SUBMIT_THRESHOLD=5
PROCTORING_IMAGE_RETENTION_DAYS=30
```

### 3. Database Initialization

```bash
# Create database with all tables
python backend/database.py

# Create default admin account (USN: ADMIN001, Password: admin123)
python backend/seed_admin.py

# Insert 6 pre-defined courses
python backend/seed_courses.py
```

### 4. Start Backend Server

```bash
python backend/app.py
```

Server runs on: **http://localhost:5000**

### 5. Test Backend API

```bash
# Health check
curl http://localhost:5000/api/health

# Register a test student
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "usn": "1CR20CS001",
    "name": "Test Student",
    "email": "test@example.com",
    "password": "test123",
    "branch": "CSE",
    "year": 3,
    "cgpa": 8.5,
    "phone": "9876543210"
  }'

# Login (save cookies)
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -c cookies.txt \
  -d '{"usn": "1CR20CS001", "password": "test123"}'

# Get courses (authenticated)
curl http://localhost:5000/api/student/courses -b cookies.txt
```

## Frontend Implementation Guide

### Priority 1: Essential Pages

The following pages are critical for basic functionality:

#### 1. Login/Registration Page (`frontend/index.html`)

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SkillSpark Pro - Login</title>
    <link rel="stylesheet" href="css/styles.css">
</head>
<body>
    <div class="login-container">
        <div class="login-card">
            <h1>SkillSpark Pro</h1>
            <p>Placement, Training & Assessment System</p>

            <div class="tabs">
                <button class="tab active" onclick="showTab('login')">Login</button>
                <button class="tab" onclick="showTab('register')">Register</button>
            </div>

            <div id="error-container"></div>
            <div id="success-container"></div>

            <!-- Login Form -->
            <form id="login-form" class="tab-content active">
                <div class="form-group">
                    <label>USN</label>
                    <input type="text" id="login-usn" required>
                </div>
                <div class="form-group">
                    <label>Password</label>
                    <input type="password" id="login-password" required>
                </div>
                <button type="submit" id="login-btn">Login</button>
            </form>

            <!-- Register Form -->
            <form id="register-form" class="tab-content">
                <div class="form-group">
                    <label>USN</label>
                    <input type="text" id="register-usn" maxlength="10" required>
                </div>
                <div class="form-group">
                    <label>Name</label>
                    <input type="text" id="register-name" required>
                </div>
                <div class="form-group">
                    <label>Email</label>
                    <input type="email" id="register-email" required>
                </div>
                <div class="form-group">
                    <label>Password</label>
                    <input type="password" id="register-password" minlength="6" required>
                </div>
                <div class="form-group">
                    <label>Branch</label>
                    <select id="register-branch" required>
                        <option value="CSE">Computer Science (CSE)</option>
                        <option value="ISE">Information Science (ISE)</option>
                        <option value="ECE">Electronics & Communication (ECE)</option>
                        <option value="MECH">Mechanical (MECH)</option>
                        <option value="CIVIL">Civil (CIVIL)</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Year</label>
                    <select id="register-year" required>
                        <option value="1">1st Year</option>
                        <option value="2">2nd Year</option>
                        <option value="3">3rd Year</option>
                        <option value="4">4th Year</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>CGPA</label>
                    <input type="number" id="register-cgpa" min="0" max="10" step="0.01" required>
                </div>
                <div class="form-group">
                    <label>Phone</label>
                    <input type="tel" id="register-phone" maxlength="10" required>
                </div>
                <button type="submit" id="register-btn">Register</button>
            </form>
        </div>
    </div>

    <script src="js/common.js"></script>
    <script src="js/auth.js"></script>
</body>
</html>
```

#### 2. Authentication JavaScript (`frontend/js/auth.js`)

```javascript
// Handle tab switching
function showTab(tabName) {
    const tabs = document.querySelectorAll('.tab');
    const contents = document.querySelectorAll('.tab-content');

    tabs.forEach(tab => tab.classList.remove('active'));
    contents.forEach(content => content.classList.remove('active'));

    if (tabName === 'login') {
        tabs[0].classList.add('active');
        document.getElementById('login-form').classList.add('active');
    } else {
        tabs[1].classList.add('active');
        document.getElementById('register-form').classList.add('active');
    }

    clearMessages();
}

// Handle login
document.getElementById('login-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    clearMessages();

    const usn = document.getElementById('login-usn').value;
    const password = document.getElementById('login-password').value;

    setButtonLoading('login-btn', true, 'Logging in...');

    try {
        const data = await apiCall('/auth/login', {
            method: 'POST',
            body: JSON.stringify({ usn, password })
        });

        // Redirect based on role
        if (data.user.role === 'student') {
            window.location.href = 'student/dashboard.html';
        } else {
            window.location.href = 'admin/dashboard.html';
        }

    } catch (error) {
        showError(error.message);
        setButtonLoading('login-btn', false);
    }
});

// Handle registration
document.getElementById('register-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    clearMessages();

    const data = {
        usn: document.getElementById('register-usn').value,
        name: document.getElementById('register-name').value,
        email: document.getElementById('register-email').value,
        password: document.getElementById('register-password').value,
        branch: document.getElementById('register-branch').value,
        year: parseInt(document.getElementById('register-year').value),
        cgpa: parseFloat(document.getElementById('register-cgpa').value),
        phone: document.getElementById('register-phone').value
    };

    setButtonLoading('register-btn', true, 'Registering...');

    try {
        const response = await apiCall('/auth/register', {
            method: 'POST',
            body: JSON.stringify(data)
        });

        // Auto-login after registration
        window.location.href = 'student/dashboard.html';

    } catch (error) {
        showError(error.message);
        setButtonLoading('register-btn', false);
    }
});
```

### Priority 2: Student Dashboard

Create `frontend/student/dashboard.html` with stats cards, course list, and upcoming exams.

### Priority 3: Basic Styling

Create `frontend/css/styles.css` with:
- Clean, corporate design
- Responsive layout
- Form styling
- Button states
- Alert boxes

## File Structure Reference

```
Skillsparkpro/
├── backend/ (✅ COMPLETE)
│   ├── app.py
│   ├── auth.py
│   ├── students.py
│   ├── jobs.py
│   ├── exams.py
│   ├── proctoring.py
│   ├── admin.py
│   ├── database.py
│   ├── config.py
│   ├── middleware.py
│   ├── utils.py
│   ├── seed_admin.py
│   └── seed_courses.py
│
├── frontend/ (⏳ 30% COMPLETE)
│   ├── index.html (⏳ NEEDED)
│   ├── student/ (⏳ NEEDED - 8 files)
│   ├── admin/ (⏳ NEEDED - 7 files)
│   ├── css/
│   │   └── styles.css (⏳ NEEDED)
│   └── js/
│       ├── common.js (✅ DONE)
│       ├── auth.js (⏳ NEEDED)
│       └── ... (⏳ NEEDED - 5 more files)
│
├── requirements.txt (✅ DONE)
├── .env.example (✅ DONE)
├── .gitignore (✅ DONE)
├── README.md (✅ DONE)
├── IMPLEMENTATION_STATUS.md (✅ DONE)
└── SETUP_GUIDE.md (✅ THIS FILE)
```

## API Endpoints Reference

All endpoints are fully functional:

### Authentication
- `POST /api/auth/register` - Register student
- `POST /api/auth/login` - Login
- `POST /api/auth/logout` - Logout
- `GET /api/auth/session` - Check session

### Student
- `GET /api/student/profile` - Get profile
- `PUT /api/student/profile` - Update profile
- `GET /api/student/courses` - List courses with enrollment
- `POST /api/student/courses/{id}/enroll` - Enroll
- `PUT /api/student/courses/{id}/progress` - Update progress

### Jobs
- `GET /api/jobs` - List jobs (filtered by eligibility for students)
- `POST /api/jobs` - Create job (admin)
- `POST /api/jobs/{id}/apply` - Apply to job
- `GET /api/jobs/applications` - Get my applications
- `PUT /api/jobs/applications/{id}/status` - Update status (admin)

### Exams
- `GET /api/exams` - List exams
- `POST /api/exams` - Create exam (admin)
- `POST /api/exams/{id}/questions` - Add question (admin)
- `PUT /api/exams/{id}/publish` - Publish exam (admin)
- `POST /api/exams/{id}/start` - Start exam
- `POST /api/exams/{id}/submit` - Submit answers
- `GET /api/exams/{id}/results` - Get results
- `PUT /api/exams/answers/{id}/evaluate` - Evaluate (admin)

### Proctoring
- `POST /api/proctoring/violation` - Log violation
- `POST /api/proctoring/frame` - Upload frame for analysis
- `GET /api/proctoring/logs/{id}` - Get logs (admin)

### Admin
- `GET /api/admin/students` - List all students
- `GET /api/admin/applications?job_id=X` - Get applications
- `GET /api/admin/exams/flagged` - Get flagged exams
- `GET /api/admin/exams/{id}/results` - Get all results
- `GET /api/admin/student/{id}/details` - Student details

## Testing the Implementation

### 1. Backend Functionality Test

```python
# Test script: test_api.py
import requests

BASE_URL = "http://localhost:5000/api"
session = requests.Session()

# Test registration
register_data = {
    "usn": "1CR20CS001",
    "name": "Test Student",
    "email": "test@example.com",
    "password": "test123",
    "branch": "CSE",
    "year": 3,
    "cgpa": 8.5,
    "phone": "9876543210"
}

response = session.post(f"{BASE_URL}/auth/register", json=register_data)
print(f"Register: {response.status_code}")

# Test login
login_data = {"usn": "ADMIN001", "password": "admin123"}
response = session.post(f"{BASE_URL}/auth/login", json=login_data)
print(f"Login: {response.status_code}")

# Test creating a job (admin)
job_data = {
    "company_name": "TechCorp",
    "job_title": "Software Engineer",
    "description": "Full stack role",
    "eligibility_cgpa": 7.0,
    "eligibility_branches": "CSE,ISE",
    "max_backlogs": 0,
    "salary_package": "6-8 LPA",
    "job_type": "full_time",
    "last_date": "2026-12-31"
}

response = session.post(f"{BASE_URL}/jobs", json=job_data)
print(f"Create Job: {response.status_code}")
```

### 2. Manual Testing Checklist

- [ ] Backend server starts without errors
- [ ] Health endpoint returns 200
- [ ] Can register new student
- [ ] Can login with student credentials
- [ ] Can login with admin credentials (ADMIN001/admin123)
- [ ] Session persists across requests
- [ ] Can fetch courses
- [ ] Can enroll in course
- [ ] Admin can create job posting
- [ ] Student can view eligible jobs
- [ ] Student can apply to job
- [ ] Admin can create exam
- [ ] Admin can add questions
- [ ] Student can start exam
- [ ] Proctoring violation logging works
- [ ] Webcam frame analysis works (if AI enabled)

## Next Steps for Completion

### Immediate (Priority 1)
1. Create `frontend/index.html` (login page)
2. Create `frontend/js/auth.js` (login logic)
3. Create `frontend/css/styles.css` (basic styling)
4. Test login/registration flow

### Short-term (Priority 2)
1. Create student dashboard page
2. Create courses page with enrollment
3. Create jobs page with application
4. Create exam listing page

### Medium-term (Priority 3)
1. Build exam interface with timer
2. Implement JavaScript proctoring
3. Create admin pages
4. Test complete workflows

### Long-term (Priority 4)
1. Add course content (learning materials)
2. Polish UI/UX
3. Comprehensive testing
4. Performance optimization

## Troubleshooting

### Database Issues
```bash
# Reset database
rm backend/database.db
python backend/database.py
python backend/seed_admin.py
python backend/seed_courses.py
```

### CORS Issues
- Backend already configured for CORS with `origins=["*"]`
- If issues persist, check browser console for specific errors

### AI Library Issues
```bash
# If OpenCV fails
pip uninstall opencv-python
pip install opencv-python-headless

# If MediaPipe fails (continue without eye tracking)
# System will gracefully degrade

# If YOLO fails (continue without object detection)
# System will gracefully degrade
```

### Session Issues
- Sessions stored in `flask_session/` directory
- Delete directory to reset all sessions
- Default session lifetime: 24 hours

## Deployment Notes

### Production Checklist
- [ ] Change SECRET_KEY to strong random value
- [ ] Set `FLASK_ENV=production`
- [ ] Use PostgreSQL instead of SQLite
- [ ] Use Redis for sessions
- [ ] Enable HTTPS (set SESSION_COOKIE_SECURE=True)
- [ ] Implement rate limiting
- [ ] Add logging and monitoring
- [ ] Secure code execution (Docker sandbox)
- [ ] Regular database backups
- [ ] Prune old proctoring images

### Recommended Production Stack
- **Web Server**: Nginx
- **WSGI Server**: Gunicorn
- **Database**: PostgreSQL
- **Session Store**: Redis
- **File Storage**: AWS S3 (for proctoring images)
- **Monitoring**: Prometheus + Grafana

## Support & Resources

- **Backend API**: Fully functional and documented
- **Sample Code**: See HTML/JS templates above
- **API Testing**: Use curl or Postman
- **Database**: SQLite Browser to inspect data
- **Logs**: Check terminal where Flask is running

---

**Implementation Progress**: ~65% Complete
**Estimated Time to Completion**: 15-20 hours (frontend development)

**Last Updated**: 2026-02-14
