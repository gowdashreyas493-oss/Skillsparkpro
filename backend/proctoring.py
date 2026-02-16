from flask import Blueprint, request, jsonify, session
from database import get_db_connection
from middleware import require_student, require_admin
from config import Config
from datetime import datetime
import json
import os
import cv2
import numpy as np

# Try to import AI libraries with graceful degradation
try:
    import mediapipe as mp
    MEDIAPIPE_AVAILABLE = True
except ImportError:
    MEDIAPIPE_AVAILABLE = False
    print("Warning: MediaPipe not available. Eye tracking disabled.")

try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False
    print("Warning: YOLO not available. Object detection disabled.")

proctoring_bp = Blueprint('proctoring', __name__)

# Initialize face detection
cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
face_cascade = cv2.CascadeClassifier(cascade_path)

# Initialize MediaPipe Face Mesh if available
if MEDIAPIPE_AVAILABLE:
    mp_face_mesh = mp.solutions.face_mesh
    face_mesh = mp_face_mesh.FaceMesh(
        max_num_faces=2,
        refine_landmarks=True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )

# Initialize YOLO if available
yolo_model = None
if YOLO_AVAILABLE and Config.AI_PROCTORING_ENABLED:
    try:
        yolo_model = YOLO('yolov8n.pt')
        print("YOLO model loaded successfully")
    except Exception as e:
        print(f"Warning: Failed to load YOLO model: {e}")
        YOLO_AVAILABLE = False

def detect_faces(image_bytes):
    """Detect faces in image using OpenCV"""
    try:
        # Convert bytes to numpy array
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if img is None:
            return {"face_count": 0, "face_detected": False, "error": "Invalid image"}

        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Detect faces
        faces = face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30)
        )

        face_count = len(faces)

        return {
            "face_count": face_count,
            "face_detected": face_count > 0,
            "faces": faces.tolist() if len(faces) > 0 else []
        }

    except Exception as e:
        return {"face_count": 0, "face_detected": False, "error": str(e)}

def track_eye_gaze(image_bytes):
    """Track eye gaze using MediaPipe Face Mesh"""
    if not MEDIAPIPE_AVAILABLE:
        return {"looking_at_screen": True, "confidence": 0.0, "disabled": True}

    try:
        # Convert bytes to numpy array
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if img is None:
            return {"looking_at_screen": True, "confidence": 0.0, "error": "Invalid image"}

        # Convert to RGB
        rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        # Process image
        results = face_mesh.process(rgb_img)

        if not results.multi_face_landmarks:
            return {"looking_at_screen": False, "confidence": 0.0, "no_landmarks": True}

        # Simple gaze detection based on face landmarks
        # In a full implementation, this would calculate gaze direction
        # For now, we assume looking at screen if face is detected
        looking_at_screen = True
        confidence = 0.8

        return {
            "looking_at_screen": looking_at_screen,
            "gaze_direction": "center",
            "confidence": confidence
        }

    except Exception as e:
        return {"looking_at_screen": True, "confidence": 0.0, "error": str(e)}

def detect_objects(image_bytes):
    """Detect suspicious objects using YOLO"""
    if not YOLO_AVAILABLE or yolo_model is None:
        return {"objects_detected": [], "suspicious": False, "disabled": True}

    try:
        # Convert bytes to numpy array
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if img is None:
            return {"objects_detected": [], "suspicious": False, "error": "Invalid image"}

        # Run YOLO detection
        results = yolo_model.predict(img, conf=0.5, verbose=False)

        # Suspicious object classes
        suspicious_classes = ['cell phone', 'book', 'laptop', 'person']

        objects_detected = []
        suspicious = False

        for result in results:
            for box in result.boxes:
                class_id = int(box.cls[0])
                class_name = result.names[class_id]
                confidence = float(box.conf[0])

                if class_name in suspicious_classes:
                    objects_detected.append({
                        "object": class_name,
                        "confidence": confidence
                    })
                    suspicious = True

        return {
            "objects_detected": objects_detected,
            "suspicious": suspicious
        }

    except Exception as e:
        return {"objects_detected": [], "suspicious": False, "error": str(e)}

@proctoring_bp.route('/violation', methods=['POST'])
@require_student
def log_violation():
    """Log a proctoring violation"""
    data = request.get_json()

    if 'student_exam_id' not in data or 'violation_type' not in data:
        return jsonify({"success": False, "error": "Missing required fields"}), 400

    student_exam_id = data['student_exam_id']
    violation_type = data['violation_type']
    severity = data.get('severity', 'medium')
    details = data.get('details', '{}')

    conn = get_db_connection()
    cursor = conn.cursor()

    # Verify student_exam belongs to user
    cursor.execute('''
        SELECT * FROM student_exams
        WHERE id=? AND student_id=?
    ''', (student_exam_id, session['user_id']))

    student_exam = cursor.fetchone()
    if not student_exam:
        conn.close()
        return jsonify({"success": False, "error": "Invalid student_exam_id"}), 400

    try:
        # Log violation
        cursor.execute('''
            INSERT INTO proctoring_logs (student_exam_id, violation_type, severity, details)
            VALUES (?, ?, ?, ?)
        ''', (student_exam_id, violation_type, severity, details))

        # Increment violation count
        new_count = student_exam['violation_count'] + 1
        cursor.execute('''
            UPDATE student_exams
            SET violation_count=?
            WHERE id=?
        ''', (new_count, student_exam_id))

        # Check if should auto-submit
        auto_submitted = False
        if new_count >= Config.AUTO_SUBMIT_THRESHOLD:
            # Auto-submit exam
            cursor.execute('''
                UPDATE student_exams
                SET status='submitted', flagged_for_review=1, end_time=CURRENT_TIMESTAMP
                WHERE id=?
            ''', (student_exam_id,))
            auto_submitted = True

        conn.commit()
        conn.close()

        response = {
            "success": True,
            "message": "Violation logged",
            "violation_count": new_count
        }

        if auto_submitted:
            response["auto_submitted"] = True
            response["message"] = "Exam auto-submitted due to excessive violations"
        elif new_count >= Config.AUTO_SUBMIT_THRESHOLD - 1:
            response["warning"] = f"Warning: One more violation will auto-submit your exam"
        else:
            response["warning"] = f"Warning: You have {new_count} violations. Exam may be auto-submitted at {Config.AUTO_SUBMIT_THRESHOLD} violations."

        return jsonify(response), 201

    except Exception as e:
        conn.close()
        return jsonify({"success": False, "error": str(e)}), 500

@proctoring_bp.route('/frame', methods=['POST'])
@require_student
def analyze_frame():
    """Upload webcam frame for AI analysis"""
    if 'frame' not in request.files:
        return jsonify({"success": False, "error": "No frame provided"}), 400

    if 'student_exam_id' not in request.form:
        return jsonify({"success": False, "error": "Missing student_exam_id"}), 400

    student_exam_id = request.form['student_exam_id']
    frame_file = request.files['frame']

    # Read frame bytes
    frame_bytes = frame_file.read()

    # Run AI analysis if enabled
    if Config.AI_PROCTORING_ENABLED:
        # Face detection
        face_result = detect_faces(frame_bytes)

        # Eye tracking
        eye_result = track_eye_gaze(frame_bytes)

        # Object detection
        object_result = detect_objects(frame_bytes)

        # Compile analysis
        analysis = {
            "face_count": face_result.get("face_count", 0),
            "face_detected": face_result.get("face_detected", False),
            "looking_at_screen": eye_result.get("looking_at_screen", True),
            "objects_detected": object_result.get("objects_detected", []),
            "suspicious": False
        }

        # Check for violations
        violation_detected = False
        violation_type = None
        severity = "medium"

        if face_result["face_count"] == 0:
            violation_detected = True
            violation_type = "no_face"
            severity = "high"
            analysis["suspicious"] = True

        elif face_result["face_count"] > 1:
            violation_detected = True
            violation_type = "multiple_faces"
            severity = "high"
            analysis["suspicious"] = True

        elif not eye_result.get("looking_at_screen", True):
            violation_detected = True
            violation_type = "looking_away"
            severity = "medium"
            analysis["suspicious"] = True

        elif object_result.get("suspicious", False):
            violation_detected = True
            # Determine specific violation type
            for obj in object_result["objects_detected"]:
                if obj["object"] == "cell phone":
                    violation_type = "mobile_detected"
                    severity = "high"
                    break
                elif obj["object"] == "book":
                    violation_type = "book_detected"
                    severity = "medium"
                    break

        # Log violation if detected
        if violation_detected and violation_type:
            conn = get_db_connection()
            cursor = conn.cursor()

            # Save frame image
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            image_dir = os.path.join(os.path.dirname(__file__), 'proctoring_images', str(student_exam_id))
            os.makedirs(image_dir, exist_ok=True)

            image_path = os.path.join(image_dir, f"{timestamp}.jpg")
            with open(image_path, 'wb') as f:
                f.write(frame_bytes)

            relative_path = f"proctoring_images/{student_exam_id}/{timestamp}.jpg"

            # Log violation
            details = json.dumps(analysis)
            cursor.execute('''
                INSERT INTO proctoring_logs (student_exam_id, violation_type, severity, details, image_path)
                VALUES (?, ?, ?, ?, ?)
            ''', (student_exam_id, violation_type, severity, details, relative_path))

            # Increment violation count
            cursor.execute('''
                UPDATE student_exams
                SET violation_count = violation_count + 1
                WHERE id=?
            ''', (student_exam_id,))

            # Get updated count
            cursor.execute("SELECT violation_count FROM student_exams WHERE id=?", (student_exam_id,))
            violation_count = cursor.fetchone()['violation_count']

            conn.commit()
            conn.close()

            analysis["violation_logged"] = True
            analysis["violation_type"] = violation_type
            analysis["violation_count"] = violation_count

        return jsonify({
            "success": True,
            "analysis": analysis
        }), 200

    else:
        # AI proctoring disabled
        return jsonify({
            "success": True,
            "analysis": {
                "face_count": 1,
                "face_detected": True,
                "looking_at_screen": True,
                "objects_detected": [],
                "suspicious": False,
                "ai_disabled": True
            }
        }), 200

@proctoring_bp.route('/logs/<int:student_exam_id>', methods=['GET'])
@require_admin
def get_logs(student_exam_id):
    """Get proctoring logs for an exam attempt (Admin only)"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT * FROM proctoring_logs
        WHERE student_exam_id=?
        ORDER BY timestamp ASC
    ''', (student_exam_id,))

    logs = cursor.fetchall()

    cursor.execute('''
        SELECT violation_count, flagged_for_review FROM student_exams
        WHERE id=?
    ''', (student_exam_id,))

    exam_data = cursor.fetchone()
    conn.close()

    return jsonify({
        "success": True,
        "logs": [dict(log) for log in logs],
        "total_violations": exam_data['violation_count'] if exam_data else 0,
        "flagged_for_review": bool(exam_data['flagged_for_review']) if exam_data else False
    }), 200
