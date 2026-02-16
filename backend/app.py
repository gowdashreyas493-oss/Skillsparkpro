from flask import Flask, session
from flask_cors import CORS
from flask_session import Session
import os

# Import configuration
from config import Config

# Import blueprints
from auth import auth_bp
from students import students_bp
from jobs import jobs_bp
from exams import exams_bp
from proctoring import proctoring_bp
from admin import admin_bp

app = Flask(__name__)

# Load configuration
Config.init_app(app)

# Configure CORS for frontend (allow file:// origin and localhost)
CORS(app, supports_credentials=True, origins=["*"], allow_headers=["Content-Type"], expose_headers=["*"])

# Configure server-side sessions
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(students_bp, url_prefix='/api/student')
app.register_blueprint(jobs_bp, url_prefix='/api/jobs')
app.register_blueprint(exams_bp, url_prefix='/api/exams')
app.register_blueprint(proctoring_bp, url_prefix='/api/proctoring')
app.register_blueprint(admin_bp, url_prefix='/api/admin')

@app.route('/')
def index():
    return {
        "message": "SkillSpark Pro API",
        "version": "1.0.0",
        "status": "running"
    }

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "SkillSpark Pro API"
    }, 200

if __name__ == '__main__':
    # Ensure proctoring images directory exists
    proctoring_dir = os.path.join(os.path.dirname(__file__), 'proctoring_images')
    if not os.path.exists(proctoring_dir):
        os.makedirs(proctoring_dir)
        print(f"Created proctoring_images directory: {proctoring_dir}")

    print("=" * 60)
    print("SkillSpark Pro - Starting Backend Server")
    print("=" * 60)
    print("API Server: http://localhost:5000")
    print("Open frontend/index.html in your browser to access the application")
    print("=" * 60)

    app.run(debug=True, host='0.0.0.0', port=5000)
