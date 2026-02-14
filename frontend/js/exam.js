// Exam interface functionality

let examData = null;
let studentExamId = null;
let questions = [];
let currentQuestionIndex = 0;
let answers = {};
let codeEditors = {};
let timerInterval = null;
let endTime = null;
let proctorInstance = null;

// Parse URL parameters
const urlParams = new URLSearchParams(window.location.search);
const examId = urlParams.get('exam_id');
studentExamId = urlParams.get('student_exam_id');

// Initialize exam
document.addEventListener('DOMContentLoaded', async () => {
    if (!examId || !studentExamId) {
        alert('Invalid exam parameters');
        window.location.href = 'exams.html';
        return;
    }

    // Check session
    const user = await checkSession();
    if (!user || user.role !== 'student') {
        window.location.href = '../index.html';
        return;
    }

    // Load exam data (would normally come from start exam API response)
    await loadExam();
});

async function loadExam() {
    try {
        // In a real scenario, exam data is already loaded when starting
        // For now, we'll create a mock structure
        examData = {
            title: "Sample Exam",
            duration_minutes: 60,
            proctoring_enabled: 1,
            questions: [] // Would be populated from API
        };

        document.getElementById('exam-title').textContent = examData.title;

        // Start timer
        endTime = new Date(Date.now() + examData.duration_minutes * 60000);
        startTimer();

        // Initialize proctoring if enabled
        if (examData.proctoring_enabled) {
            proctorInstance = new ExamProctor(studentExamId);
            document.getElementById('proctoring-status').style.display = 'block';
            document.getElementById('violation-display').style.display = 'flex';
        }

        // Load questions (mock for now)
        questions = examData.questions;
        initializeQuestions();

    } catch (error) {
        alert('Failed to load exam: ' + error.message);
        window.location.href = 'exams.html';
    }
}

function initializeQuestions() {
    if (questions.length === 0) {
        document.getElementById('question-area').innerHTML = `
            <div class="question-card">
                <p class="text-center">No questions available for this exam.</p>
            </div>
        `;
        return;
    }

    // Initialize answers object
    questions.forEach(q => {
        answers[q.id] = {
            question_id: q.id,
            answer_type: q.question_type === 'mcq' ? 'mcq_option' : 'code',
            answer_value: ''
        };
    });

    // Create question navigator buttons
    const navigator = document.getElementById('question-navigator');
    navigator.innerHTML = questions.map((q, idx) => `
        <button class="question-nav-btn ${idx === 0 ? 'current' : ''}"
                onclick="navigateToQuestion(${idx})"
                id="nav-btn-${idx}">
            ${idx + 1}
        </button>
    `).join('');

    // Display first question
    displayQuestion(0);
}

function displayQuestion(index) {
    if (index < 0 || index >= questions.length) return;

    currentQuestionIndex = index;
    const question = questions[index];

    // Update navigator
    document.querySelectorAll('.question-nav-btn').forEach((btn, idx) => {
        btn.classList.remove('current');
        if (answers[questions[idx].id].answer_value) {
            btn.classList.add('answered');
        }
    });
    document.getElementById(`nav-btn-${index}`).classList.add('current');

    // Display question
    const questionArea = document.getElementById('question-area');

    if (question.question_type === 'mcq') {
        questionArea.innerHTML = `
            <div class="question-card">
                <div class="question-header">
                    <div class="question-number">Question ${index + 1} of ${questions.length}</div>
                    <span class="badge">MCQ - ${question.marks} marks</span>
                </div>
                <div class="question-text">${question.question_text}</div>
                <div class="options">
                    ${['A', 'B', 'C', 'D'].map(opt => `
                        <label class="option ${answers[question.id].answer_value === opt ? 'selected' : ''}"
                               onclick="selectOption(${question.id}, '${opt}')">
                            <input type="radio" name="q${question.id}" value="${opt}"
                                   ${answers[question.id].answer_value === opt ? 'checked' : ''}>
                            <strong>${opt}.</strong> ${question['option_' + opt.toLowerCase()]}
                        </label>
                    `).join('')}
                </div>
                <div style="display: flex; gap: 12px; margin-top: 24px;">
                    ${index > 0 ? '<button class="btn btn-secondary" onclick="navigateToQuestion(' + (index - 1) + ')">Previous</button>' : ''}
                    ${index < questions.length - 1 ? '<button class="btn btn-primary" onclick="navigateToQuestion(' + (index + 1) + ')">Next</button>' : ''}
                </div>
            </div>
        `;
    } else {
        // Coding question
        questionArea.innerHTML = `
            <div class="question-card">
                <div class="question-header">
                    <div class="question-number">Question ${index + 1} of ${questions.length}</div>
                    <span class="badge">Coding (${question.language}) - ${question.marks} marks</span>
                </div>
                <div class="question-text">${question.question_text}</div>
                <div style="margin-top: 20px;">
                    <label style="font-weight: 600; margin-bottom: 8px; display: block;">Your Code:</label>
                    <textarea id="code-editor-${question.id}" style="width: 100%; height: 300px; font-family: monospace;">${answers[question.id].answer_value}</textarea>
                </div>
                <div style="display: flex; gap: 12px; margin-top: 24px;">
                    ${index > 0 ? '<button class="btn btn-secondary" onclick="navigateToQuestion(' + (index - 1) + ')">Previous</button>' : ''}
                    ${index < questions.length - 1 ? '<button class="btn btn-primary" onclick="navigateToQuestion(' + (index + 1) + ')">Next</button>' : ''}
                </div>
            </div>
        `;

        // Initialize CodeMirror
        const textarea = document.getElementById(`code-editor-${question.id}`);
        const mode = question.language === 'python' ? 'python' :
                     question.language === 'java' ? 'text/x-java' : 'text/x-c++src';

        const editor = CodeMirror.fromTextArea(textarea, {
            mode: mode,
            theme: 'eclipse',
            lineNumbers: true,
            indentUnit: 4,
            tabSize: 4,
            lineWrapping: true
        });

        editor.on('change', (cm) => {
            answers[question.id].answer_value = cm.getValue();
        });

        codeEditors[question.id] = editor;
    }
}

function selectOption(questionId, option) {
    answers[questionId].answer_value = option;

    // Update UI
    document.querySelectorAll(`input[name="q${questionId}"]`).forEach(input => {
        const label = input.parentElement;
        if (input.value === option) {
            label.classList.add('selected');
        } else {
            label.classList.remove('selected');
        }
    });

    // Update navigator
    const questionIndex = questions.findIndex(q => q.id === questionId);
    document.getElementById(`nav-btn-${questionIndex}`).classList.add('answered');
}

function navigateToQuestion(index) {
    // Save current code editor if exists
    const currentQuestion = questions[currentQuestionIndex];
    if (currentQuestion.question_type === 'coding' && codeEditors[currentQuestion.id]) {
        answers[currentQuestion.id].answer_value = codeEditors[currentQuestion.id].getValue();
    }

    displayQuestion(index);
}

function startTimer() {
    updateTimerDisplay();

    timerInterval = setInterval(() => {
        updateTimerDisplay();

        if (Date.now() >= endTime.getTime()) {
            clearInterval(timerInterval);
            alert('Time is up! Submitting exam...');
            confirmSubmit();
        }
    }, 1000);
}

function updateTimerDisplay() {
    const remaining = endTime.getTime() - Date.now();

    if (remaining <= 0) {
        document.getElementById('timer').textContent = '00:00';
        document.getElementById('timer').classList.add('warning');
        return;
    }

    const minutes = Math.floor(remaining / 60000);
    const seconds = Math.floor((remaining % 60000) / 1000);

    const display = `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
    document.getElementById('timer').textContent = display;

    if (minutes < 5) {
        document.getElementById('timer').classList.add('warning');
    }
}

function submitExam() {
    document.getElementById('submit-modal').classList.add('active');
}

function closeSubmitModal() {
    document.getElementById('submit-modal').classList.remove('active');
}

async function confirmSubmit() {
    closeSubmitModal();

    // Save all code editors
    questions.forEach(q => {
        if (q.question_type === 'coding' && codeEditors[q.id]) {
            answers[q.id].answer_value = codeEditors[q.id].getValue();
        }
    });

    // Prepare submission
    const submission = {
        student_exam_id: studentExamId,
        answers: Object.values(answers)
    };

    try {
        // Stop timer and proctoring
        if (timerInterval) clearInterval(timerInterval);
        if (proctorInstance) proctorInstance.stopProctoring();

        const result = await apiCall(`/exams/${examId}/submit`, {
            method: 'POST',
            body: JSON.stringify(submission)
        });

        alert('Exam submitted successfully!');
        window.location.href = `results.html?exam_id=${examId}`;

    } catch (error) {
        alert('Submission failed: ' + error.message);
        // Restart timer
        startTimer();
    }
}

// Handle page unload
window.addEventListener('beforeunload', (e) => {
    if (examData) {
        e.preventDefault();
        e.returnValue = 'Are you sure? Your exam progress may be lost.';
    }
});
