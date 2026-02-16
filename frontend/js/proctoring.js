// Client-side proctoring functionality

class ExamProctor {
    constructor(studentExamId) {
        this.studentExamId = studentExamId;
        this.violationCount = 0;
        this.stream = null;
        this.frameInterval = null;
        this.isFullscreen = false;

        this.initialize();
    }

    async initialize() {
        // Enable fullscreen
        this.enterFullscreen();

        // Setup event listeners
        this.setupFullscreenListener();
        this.setupTabSwitchListener();
        this.setupCopyPasteBlocker();
        this.setupNavigationBlocker();

        // Initialize webcam
        await this.initializeWebcam();
    }

    // Fullscreen enforcement
    enterFullscreen() {
        const elem = document.documentElement;
        if (elem.requestFullscreen) {
            elem.requestFullscreen().catch(() => {
                console.warn('Fullscreen request failed');
            });
        }
    }

    setupFullscreenListener() {
        document.addEventListener('fullscreenchange', () => {
            if (!document.fullscreenElement) {
                this.isFullscreen = false;
                this.logViolation('fullscreen_exit', 'medium', { message: 'Exited fullscreen mode' });
                this.updateFullscreenStatus(false);

                // Force back to fullscreen
                setTimeout(() => {
                    this.enterFullscreen();
                }, 1000);
            } else {
                this.isFullscreen = true;
                this.updateFullscreenStatus(true);
            }
        });
    }

    updateFullscreenStatus(isActive) {
        const dot = document.getElementById('fullscreen-dot');
        const status = document.getElementById('fullscreen-status');

        if (isActive) {
            dot.className = 'status-dot green';
            status.textContent = 'Fullscreen Active';
        } else {
            dot.className = 'status-dot red';
            status.textContent = 'Fullscreen Exited!';
        }
    }

    // Tab switch detection
    setupTabSwitchListener() {
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                this.logViolation('tab_switch', 'medium', { message: 'Switched to another tab' });
                this.updateTabStatus(false);
            } else {
                this.updateTabStatus(true);
            }
        });

        window.addEventListener('blur', () => {
            this.logViolation('tab_switch', 'medium', { message: 'Window lost focus' });
        });
    }

    updateTabStatus(isActive) {
        const dot = document.getElementById('tab-dot');
        const status = document.getElementById('tab-status');

        if (isActive) {
            dot.className = 'status-dot green';
            status.textContent = 'No Tab Switches';
        } else {
            dot.className = 'status-dot red';
            status.textContent = 'Tab Switch Detected!';

            setTimeout(() => {
                if (!document.hidden) {
                    dot.className = 'status-dot green';
                    status.textContent = 'No Tab Switches';
                }
            }, 3000);
        }
    }

    // Block copy/paste
    setupCopyPasteBlocker() {
        // Block right-click
        document.addEventListener('contextmenu', (e) => {
            if (!e.target.closest('.CodeMirror')) {
                e.preventDefault();
                this.showWarning('Right-click disabled during exam');
            }
        });

        // Block keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            const isCodeEditor = e.target.closest('.CodeMirror');

            // Allow in code editor
            if (isCodeEditor) return;

            // Block common shortcuts
            if ((e.ctrlKey || e.metaKey) && ['c', 'v', 'x', 'a'].includes(e.key.toLowerCase())) {
                e.preventDefault();
                this.showWarning('Copy/paste disabled during exam');
                this.logViolation('copy_paste', 'low', { key: e.key });
            }

            // Block F12 and developer tools
            if (e.key === 'F12' || ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'I')) {
                e.preventDefault();
                this.showWarning('Developer tools disabled during exam');
            }
        });
    }

    // Block navigation
    setupNavigationBlocker() {
        // Prevent back button
        history.pushState(null, null, location.href);
        window.addEventListener('popstate', () => {
            history.pushState(null, null, location.href);
            this.showWarning('Navigation blocked during exam');
        });

        // Warn on page refresh
        window.addEventListener('beforeunload', (e) => {
            e.preventDefault();
            e.returnValue = 'Are you sure? Your exam progress may be lost.';
        });
    }

    // Webcam initialization
    async initializeWebcam() {
        try {
            this.stream = await navigator.mediaDevices.getUserMedia({ video: true });

            // Start frame capture every 10 seconds
            this.frameInterval = setInterval(() => {
                this.captureAndAnalyzeFrame();
            }, 10000);

            this.updateFaceStatus(true);

        } catch (error) {
            console.error('Camera access denied:', error);
            this.showWarning('Camera access required for proctoring. Exam will be flagged for review.');
            this.updateFaceStatus(false);
            this.logViolation('camera_denied', 'high', { error: error.message });
        }
    }

    async captureAndAnalyzeFrame() {
        if (!this.stream) return;

        try {
            // Create video element
            const video = document.createElement('video');
            video.srcObject = this.stream;
            video.play();

            // Wait for video to be ready
            await new Promise(resolve => {
                video.onloadedmetadata = resolve;
            });

            // Capture frame
            const canvas = document.createElement('canvas');
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
            const ctx = canvas.getContext('2d');
            ctx.drawImage(video, 0, 0);

            // Convert to blob
            canvas.toBlob(async (blob) => {
                const formData = new FormData();
                formData.append('student_exam_id', this.studentExamId);
                formData.append('frame', blob, 'frame.jpg');

                try {
                    const result = await uploadFile('/proctoring/frame', formData);

                    if (result.analysis) {
                        this.updateFaceStatus(result.analysis.face_detected);

                        if (result.analysis.violation_logged) {
                            this.violationCount = result.analysis.violation_count;
                            this.updateViolationDisplay();
                        }
                    }
                } catch (error) {
                    console.error('Frame analysis failed:', error);
                }
            }, 'image/jpeg', 0.8);

        } catch (error) {
            console.error('Frame capture failed:', error);
        }
    }

    updateFaceStatus(detected) {
        const dot = document.getElementById('face-dot');
        const status = document.getElementById('face-status');

        if (detected) {
            dot.className = 'status-dot green';
            status.textContent = 'Face Detected';
        } else {
            dot.className = 'status-dot red';
            status.textContent = 'No Face Detected!';
        }
    }

    // Log violation
    async logViolation(type, severity, details) {
        try {
            const result = await apiCall('/proctoring/violation', {
                method: 'POST',
                body: JSON.stringify({
                    student_exam_id: this.studentExamId,
                    violation_type: type,
                    severity: severity,
                    details: JSON.stringify(details)
                })
            });

            this.violationCount = result.violation_count;
            this.updateViolationDisplay();

            if (result.auto_submitted) {
                alert('Exam auto-submitted due to excessive violations.');
                window.location.href = 'results.html';
            } else if (result.warning) {
                this.showWarning(result.warning);
            }

        } catch (error) {
            console.error('Failed to log violation:', error);
        }
    }

    updateViolationDisplay() {
        document.getElementById('violation-count').textContent = this.violationCount;

        if (this.violationCount >= 4) {
            document.getElementById('violation-display').style.background = '#fee2e2';
            document.getElementById('violation-display').style.color = '#991b1b';
        }
    }

    showWarning(message) {
        // Create temporary warning banner
        const banner = document.createElement('div');
        banner.style.cssText = `
            position: fixed;
            top: 70px;
            left: 50%;
            transform: translateX(-50%);
            background: #fef3c7;
            color: #92400e;
            padding: 12px 24px;
            border-radius: 6px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            z-index: 9999;
            font-weight: 600;
        `;
        banner.textContent = message;
        document.body.appendChild(banner);

        setTimeout(() => {
            banner.remove();
        }, 3000);
    }

    // Cleanup
    stopProctoring() {
        if (this.frameInterval) {
            clearInterval(this.frameInterval);
        }

        if (this.stream) {
            this.stream.getTracks().forEach(track => track.stop());
        }

        // Exit fullscreen
        if (document.exitFullscreen) {
            document.exitFullscreen().catch(() => {});
        }
    }
}
