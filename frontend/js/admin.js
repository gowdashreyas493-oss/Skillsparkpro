// Admin-specific functionality

// Load admin dashboard
async function loadAdminDashboard() {
    try {
        // Load students count
        const studentsData = await apiCall('/admin/students');

        // Load jobs
        const jobsData = await apiCall('/jobs');
        const activeJobs = jobsData.jobs.filter(j => j.status === 'active');

        // Load exams
        const examsData = await apiCall('/exams');

        // Load applications (approximate)
        let totalApplications = 0;
        for (const job of jobsData.jobs.slice(0, 5)) { // Sample first 5
            try {
                const appsData = await apiCall(`/admin/applications?job_id=${job.id}`);
                totalApplications += appsData.applications.length;
            } catch (e) {}
        }

        // Update stats
        document.getElementById('stat-students').textContent = studentsData.students.length;
        document.getElementById('stat-jobs').textContent = activeJobs.length;
        document.getElementById('stat-exams').textContent = examsData.exams.length;
        document.getElementById('stat-applications').textContent = totalApplications;

        // Display recent activity
        displayRecentActivity(studentsData.students, jobsData.jobs, examsData.exams);

    } catch (error) {
        console.error('Failed to load dashboard data:', error);
    }
}

function displayRecentActivity(students, jobs, exams) {
    const container = document.getElementById('recent-activity');

    const recentStudents = students.slice(0, 3);
    const recentJobs = jobs.slice(0, 2);

    container.innerHTML = `
        <h3 style="margin-bottom: 16px;">Recent Students</h3>
        ${recentStudents.map(s => `
            <div style="padding: 12px; background: #f9fafb; border-radius: 6px; margin-bottom: 8px;">
                <strong>${s.name}</strong> (${s.usn}) - ${s.branch}, Year ${s.year}
            </div>
        `).join('')}

        <h3 style="margin-top: 24px; margin-bottom: 16px;">Recent Jobs</h3>
        ${recentJobs.map(j => `
            <div style="padding: 12px; background: #f9fafb; border-radius: 6px; margin-bottom: 8px;">
                <strong>${j.company_name}</strong> - ${j.job_title}
            </div>
        `).join('')}
    `;
}

// Load students page
async function loadStudentsPage() {
    try {
        const data = await apiCall('/admin/students');
        displayStudentsList(data.students);
    } catch (error) {
        showError('Failed to load students: ' + error.message);
    }
}

function displayStudentsList(students) {
    const container = document.getElementById('students-table');

    container.innerHTML = `
        <table>
            <thead>
                <tr>
                    <th>USN</th>
                    <th>Name</th>
                    <th>Branch</th>
                    <th>Year</th>
                    <th>CGPA</th>
                    <th>Backlogs</th>
                    <th>Action</th>
                </tr>
            </thead>
            <tbody>
                ${students.map(s => `
                    <tr>
                        <td><strong>${s.usn}</strong></td>
                        <td>${s.name}</td>
                        <td>${s.branch}</td>
                        <td>${s.year}</td>
                        <td>${s.cgpa}</td>
                        <td>${s.backlogs}</td>
                        <td>
                            <button class="btn btn-sm btn-primary" onclick="viewStudentDetails(${s.id})">
                                View Details
                            </button>
                        </td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;
}

async function viewStudentDetails(studentId) {
    try {
        const data = await apiCall(`/admin/student/${studentId}/details`);
        displayStudentDetailsModal(data);
    } catch (error) {
        showError('Failed to load student details: ' + error.message);
    }
}

function displayStudentDetailsModal(data) {
    const student = data.student;

    const modal = document.createElement('div');
    modal.className = 'modal active';
    modal.innerHTML = `
        <div class="modal-content" style="max-width: 600px;">
            <div class="modal-header">
                <h2>${student.name} (${student.usn})</h2>
            </div>
            <div style="margin: 20px 0;">
                <p><strong>Email:</strong> ${student.email}</p>
                <p><strong>Branch:</strong> ${student.branch}, Year ${student.year}</p>
                <p><strong>CGPA:</strong> ${student.cgpa} | <strong>Backlogs:</strong> ${student.backlogs}</p>
                <p><strong>Skills:</strong> ${student.skills || 'Not specified'}</p>

                <h3 style="margin-top: 20px;">Enrolled Courses (${data.courses.length})</h3>
                ${data.courses.map(c => `
                    <div style="padding: 8px; background: #f9fafb; margin: 4px 0; border-radius: 4px;">
                        ${c.title} - ${c.progress_percentage}% (${c.status})
                    </div>
                `).join('')}

                <h3 style="margin-top: 20px;">Job Applications (${data.applications.length})</h3>
                ${data.applications.map(a => `
                    <div style="padding: 8px; background: #f9fafb; margin: 4px 0; border-radius: 4px;">
                        ${a.company_name} - ${a.job_title} (<span class="status-badge ${a.status}">${a.status}</span>)
                    </div>
                `).join('')}

                <h3 style="margin-top: 20px;">Exam History (${data.exams.length})</h3>
                ${data.exams.map(e => `
                    <div style="padding: 8px; background: #f9fafb; margin: 4px 0; border-radius: 4px;">
                        ${e.title} - Score: ${e.total_score}/${e.percentage.toFixed(1)}% (<span class="status-badge ${e.result}">${e.result}</span>)
                    </div>
                `).join('')}
            </div>
            <div class="modal-footer">
                <button class="btn btn-secondary" onclick="this.closest('.modal').remove()">Close</button>
            </div>
        </div>
    `;

    document.body.appendChild(modal);
}

// Create job
async function createJob(event) {
    event.preventDefault();

    const data = {
        company_name: document.getElementById('company-name').value.trim(),
        job_title: document.getElementById('job-title').value.trim(),
        description: document.getElementById('job-description').value.trim(),
        eligibility_cgpa: parseFloat(document.getElementById('eligibility-cgpa').value),
        eligibility_branches: Array.from(document.getElementById('eligibility-branches').selectedOptions)
            .map(opt => opt.value).join(','),
        max_backlogs: parseInt(document.getElementById('max-backlogs').value),
        salary_package: document.getElementById('salary-package').value.trim(),
        job_type: document.getElementById('job-type').value,
        last_date: document.getElementById('last-date').value
    };

    try {
        await apiCall('/jobs', {
            method: 'POST',
            body: JSON.stringify(data)
        });

        showSuccess('Job posted successfully!');
        event.target.reset();
        setTimeout(() => window.location.reload(), 1500);

    } catch (error) {
        showError('Failed to create job: ' + error.message);
    }
}

// Load applications for a job
async function loadApplicationsForJob() {
    const jobId = document.getElementById('job-selector').value;
    if (!jobId) {
        document.getElementById('applications-table').innerHTML = '';
        return;
    }

    try {
        const data = await apiCall(`/admin/applications?job_id=${jobId}`);
        displayApplicationsTable(data.applications);
    } catch (error) {
        showError('Failed to load applications: ' + error.message);
    }
}

function displayApplicationsTable(applications) {
    const container = document.getElementById('applications-table');

    if (applications.length === 0) {
        container.innerHTML = '<p class="text-center" style="padding: 40px; color: #6b7280;">No applications yet</p>';
        return;
    }

    container.innerHTML = `
        <table>
            <thead>
                <tr>
                    <th>USN</th>
                    <th>Name</th>
                    <th>Branch</th>
                    <th>CGPA</th>
                    <th>Backlogs</th>
                    <th>Status</th>
                    <th>Action</th>
                </tr>
            </thead>
            <tbody>
                ${applications.map(app => `
                    <tr>
                        <td>${app.usn}</td>
                        <td>${app.name}</td>
                        <td>${app.branch}</td>
                        <td>${app.cgpa}</td>
                        <td>${app.backlogs}</td>
                        <td>
                            <select id="status-${app.id}" class="form-control">
                                <option value="applied" ${app.status === 'applied' ? 'selected' : ''}>Applied</option>
                                <option value="shortlisted" ${app.status === 'shortlisted' ? 'selected' : ''}>Shortlisted</option>
                                <option value="rejected" ${app.status === 'rejected' ? 'selected' : ''}>Rejected</option>
                                <option value="selected" ${app.status === 'selected' ? 'selected' : ''}>Selected</option>
                            </select>
                        </td>
                        <td>
                            <button class="btn btn-sm btn-primary" onclick="updateApplicationStatus(${app.id})">Update</button>
                        </td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;
}

async function updateApplicationStatus(appId) {
    const newStatus = document.getElementById(`status-${appId}`).value;

    try {
        await apiCall(`/jobs/applications/${appId}/status`, {
            method: 'PUT',
            body: JSON.stringify({ status: newStatus })
        });

        showSuccess('Status updated successfully!');

    } catch (error) {
        showError('Failed to update status: ' + error.message);
    }
}

// Create exam
async function createExam(event) {
    event.preventDefault();

    const data = {
        title: document.getElementById('exam-title').value.trim(),
        exam_type: document.getElementById('exam-type').value,
        duration_minutes: parseInt(document.getElementById('duration').value),
        total_marks: parseInt(document.getElementById('total-marks').value),
        passing_marks: parseInt(document.getElementById('passing-marks').value),
        instructions: document.getElementById('instructions').value.trim(),
        scheduled_date: document.getElementById('scheduled-date').value,
        proctoring_enabled: document.getElementById('proctoring-enabled').checked ? 1 : 0
    };

    try {
        const result = await apiCall('/exams', {
            method: 'POST',
            body: JSON.stringify(data)
        });

        showSuccess('Exam created successfully! Add questions now.');
        // Store exam ID for adding questions
        sessionStorage.setItem('current_exam_id', result.exam.id);
        document.getElementById('exam-form').style.display = 'none';
        document.getElementById('questions-section').style.display = 'block';

    } catch (error) {
        showError('Failed to create exam: ' + error.message);
    }
}

// Add question to exam
async function addQuestion(type) {
    const examId = sessionStorage.getItem('current_exam_id');
    if (!examId) {
        showError('No exam selected');
        return;
    }

    let data = {};

    if (type === 'mcq') {
        data = {
            question_type: 'mcq',
            question_text: prompt('Question Text:'),
            option_a: prompt('Option A:'),
            option_b: prompt('Option B:'),
            option_c: prompt('Option C:'),
            option_d: prompt('Option D:'),
            correct_answer: prompt('Correct Answer (A/B/C/D):').toUpperCase(),
            marks: parseInt(prompt('Marks:')),
            difficulty: prompt('Difficulty (easy/medium/hard):')
        };
    } else {
        data = {
            question_type: 'coding',
            question_text: prompt('Question Text:'),
            language: prompt('Language (python/java/cpp):'),
            marks: parseInt(prompt('Marks:')),
            difficulty: prompt('Difficulty (easy/medium/hard):'),
            test_cases: [] // Simplified - would need proper form
        };
    }

    try {
        await apiCall(`/exams/${examId}/questions`, {
            method: 'POST',
            body: JSON.stringify(data)
        });

        showSuccess('Question added!');

    } catch (error) {
        showError('Failed to add question: ' + error.message);
    }
}

// Publish exam
async function publishExam() {
    const examId = sessionStorage.getItem('current_exam_id');
    if (!examId) {
        showError('No exam selected');
        return;
    }

    try {
        await apiCall(`/exams/${examId}/publish`, { method: 'PUT' });
        showSuccess('Exam published! Students can now see it.');
        sessionStorage.removeItem('current_exam_id');
        setTimeout(() => window.location.reload(), 2000);

    } catch (error) {
        showError('Failed to publish exam: ' + error.message);
    }
}

// View proctoring logs
async function viewProctoringLogs(studentExamId) {
    try {
        const data = await apiCall(`/proctoring/logs/${studentExamId}`);
        displayProctoringLogsModal(data);
    } catch (error) {
        showError('Failed to load logs: ' + error.message);
    }
}

function displayProctoringLogsModal(data) {
    const modal = document.createElement('div');
    modal.className = 'modal active';
    modal.innerHTML = `
        <div class="modal-content" style="max-width: 700px;">
            <div class="modal-header">
                <h2>Proctoring Logs</h2>
                <p>Total Violations: ${data.total_violations} | Flagged: ${data.flagged_for_review ? 'Yes' : 'No'}</p>
            </div>
            <div style="margin: 20px 0; max-height: 400px; overflow-y: auto;">
                <table style="width: 100%; font-size: 13px;">
                    <thead>
                        <tr>
                            <th>Time</th>
                            <th>Type</th>
                            <th>Severity</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${data.logs.map(log => `
                            <tr>
                                <td>${formatDateTime(log.timestamp)}</td>
                                <td>${log.violation_type}</td>
                                <td>
                                    <span class="status-badge ${log.severity === 'high' ? 'fail' : log.severity === 'medium' ? 'pending' : 'pass'}">
                                        ${log.severity.toUpperCase()}
                                    </span>
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
            <div class="modal-footer">
                <button class="btn btn-secondary" onclick="this.closest('.modal').remove()">Close</button>
            </div>
        </div>
    `;

    document.body.appendChild(modal);
}
