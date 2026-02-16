import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Application configuration from environment variables"""

    # Flask configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')

    # Session configuration
    SESSION_TYPE = 'filesystem'
    SESSION_PERMANENT = False
    SESSION_USE_SIGNER = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = 86400  # 24 hours in seconds

    # AI Proctoring configuration
    AI_PROCTORING_ENABLED = os.getenv('AI_PROCTORING_ENABLED', 'True').lower() == 'true'
    FRAME_CAPTURE_INTERVAL = int(os.getenv('FRAME_CAPTURE_INTERVAL', '10'))
    AUTO_SUBMIT_THRESHOLD = int(os.getenv('AUTO_SUBMIT_THRESHOLD', '5'))
    PROCTORING_IMAGE_RETENTION_DAYS = int(os.getenv('PROCTORING_IMAGE_RETENTION_DAYS', '30'))

    # Code execution configuration
    CODE_EXECUTION_TIMEOUT = 5  # seconds
    MAX_CODE_OUTPUT_LENGTH = 1000  # characters

    @staticmethod
    def init_app(app):
        """Initialize app with configuration"""
        app.config.from_object(Config)
