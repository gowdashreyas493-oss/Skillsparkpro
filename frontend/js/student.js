// Student-specific functionality

// Load dashboard data
async function loadDashboardData() {
    try {
        // Load profile for stats
        const profile = await apiCall('/student/profile');

        // Load courses
        const coursesData = await apiCall('/student/courses');
        const enrolledCourses = coursesData.courses.filter(c => c.enrolled);

        // Load applications
        const appsData = await apiCall('/jobs/applications');

        // Load exams
        const examsData = await apiCall('/exams');
        const completedExams = examsData.exams.filter(e => e.attempt_status === 'evaluated');

        // Calculate average score
        let avgScore = 0;
        if (completedExams.length > 0) {
            // Would need to fetch results for each exam - simplified here
            avgScore = '-';
        }

        // Update stats
        document.getElementById('stat-courses').textContent = enrolledCourses.length;
        document.getElementById('stat-jobs').textContent = appsData.applications.length;
        document.getElementById('stat-exams').textContent = completedExams.length;
        document.getElementById('stat-average').textContent = avgScore;

        // Display courses
        displayDashboardCourses(enrolledCourses);

        // Display upcoming exams
        displayUpcomingExams(examsData.exams);

        // Load and display jobs
        const jobsData = await apiCall('/jobs');
        displayLatestJobs(jobsData.jobs.slice(0, 3));

    } catch (error) {
        console.error('Failed to load dashboard data:', error);
    }
}

// Display courses on dashboard
function displayDashboardCourses(courses) {
    const container = document.getElementById('courses-container');
    const noCoursesMsg = document.getElementById('no-courses');

    if (courses.length === 0) {
        container.innerHTML = '';
        container.classList.add('hidden');
        noCoursesMsg.classList.remove('hidden');
        return;
    }

    container.classList.remove('hidden');
    noCoursesMsg.classList.add('hidden');

    container.innerHTML = courses.map(course => `
        <div class="course-card">
            <span class="badge ${course.category}">${course.category}</span>
            <h3>${course.title}</h3>
            <p class="duration">${course.duration_hours} hours</p>
            <div class="progress-bar">
                <div class="progress-fill" style="width: ${course.progress_percentage}%"></div>
            </div>
            <p style="font-size: 13px; color: #6b7280; margin-top: 8px;">
                ${course.progress_percentage}% Complete
            </p>
            <button class="btn btn-primary btn-sm mt-10" onclick="continueCourse(${course.id})">
                Continue Learning
            </button>
        </div>
    `).join('');
}

// Display upcoming exams
function displayUpcomingExams(exams) {
    const container = document.getElementById('exams-container');

    const upcomingExams = exams.filter(e =>
        e.attempt_status === 'not_started' &&
        new Date(e.scheduled_date) <= new Date()
    );

    if (upcomingExams.length === 0) {
        container.innerHTML = '<p class="text-center" style="color: #6b7280; padding: 20px;">No upcoming exams</p>';
        return;
    }

    container.innerHTML = `
        <table>
            <thead>
                <tr>
                    <th>Exam</th>
                    <th>Type</th>
                    <th>Duration</th>
                    <th>Marks</th>
                    <th>Scheduled</th>
                    <th>Action</th>
                </tr>
            </thead>
            <tbody>
                ${upcomingExams.map(exam => `
                    <tr>
                        <td><strong>${exam.title}</strong></td>
                        <td><span class="badge">${exam.exam_type.toUpperCase()}</span></td>
                        <td>${exam.duration_minutes} min</td>
                        <td>${exam.total_marks}</td>
                        <td>${formatDateTime(exam.scheduled_date)}</td>
                        <td>
                            <a href="exams.html" class="btn btn-primary btn-sm">View Details</a>
                        </td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;
}

// Display latest jobs
function displayLatestJobs(jobs) {
    const container = document.getElementById('jobs-container');

    if (jobs.length === 0) {
        container.innerHTML = '<p class="text-center" style="color: #6b7280; padding: 20px;">No job postings available</p>';
        return;
    }

    container.innerHTML = jobs.map(job => `
        <div class="job-card" style="margin-bottom: 16px;">
            <h3>${job.job_title}</h3>
            <p class="company">${job.company_name}</p>
            <div class="details">
                <span>💰 ${job.salary_package}</span>
                <span>📅 Deadline: ${formatDate(job.last_date)}</span>
                <span>🎯 CGPA: ${job.eligibility_cgpa}+</span>
            </div>
            ${job.is_eligible ?
                `<span class="eligibility-badge eligible">✓ You are eligible</span>` :
                `<span class="eligibility-badge not-eligible">✗ Not eligible</span>`
            }
            <button class="btn btn-primary btn-sm mt-10" onclick="window.location.href='jobs.html'">
                View All Jobs
            </button>
        </div>
    `).join('');
}

// Continue course
function continueCourse(courseId) {
    window.location.href = `../courses/${courseId}/index.html`;
}

// Load courses page
async function loadCoursesPage() {
    try {
        const data = await apiCall('/student/courses');
        displayAllCourses(data.courses);
    } catch (error) {
        showError('Failed to load courses: ' + error.message);
    }
}

// Display all courses
function displayAllCourses(courses) {
    const container = document.getElementById('courses-grid');

    container.innerHTML = courses.map(course => `
        <div class="course-card">
            <span class="badge ${course.category}">${course.category}</span>
            <h3>${course.title}</h3>
            <p class="duration">${course.duration_hours} hours</p>
            <p style="font-size: 14px; color: #6b7280; margin: 12px 0;">${course.description}</p>

            ${course.enrolled ? `
                <div class="progress-bar">
                    <div class="progress-fill" style="width: ${course.progress_percentage}%"></div>
                </div>
                <p style="font-size: 13px; color: #6b7280; margin-top: 8px;">
                    ${course.progress_percentage}% Complete
                </p>
                ${course.status === 'completed' ?
                    '<span class="status-badge pass">✓ Completed</span>' :
                    `<button class="btn btn-primary btn-sm mt-10" onclick="continueCourse(${course.id})">Continue</button>`
                }
            ` : `
                <button class="btn btn-primary mt-10" onclick="enrollCourse(${course.id})">Enroll Now</button>
            `}
        </div>
    `).join('');
}

// Enroll in course
async function enrollCourse(courseId) {
    try {
        await apiCall(`/student/courses/${courseId}/enroll`, { method: 'POST' });
        showSuccess('Enrolled successfully!');
        setTimeout(() => window.location.reload(), 1000);
    } catch (error) {
        showError('Enrollment failed: ' + error.message);
    }
}

// Load jobs page
async function loadJobsPage() {
    try {
        const data = await apiCall('/jobs');
        displayJobs(data.jobs);
    } catch (error) {
        showError('Failed to load jobs: ' + error.message);
    }
}

// Display jobs
function displayJobs(jobs) {
    const container = document.getElementById('jobs-grid');

    if (jobs.length === 0) {
        container.innerHTML = '<p class="text-center" style="color: #6b7280; padding: 40px;">No job postings available</p>';
        return;
    }

    container.innerHTML = jobs.map(job => `
        <div class="job-card">
            <h3>${job.job_title}</h3>
            <p class="company">${job.company_name}</p>
            <p style="margin: 12px 0; color: #6b7280;">${job.description || 'No description available'}</p>

            <div class="details">
                <span>💰 ${job.salary_package}</span>
                <span>📅 Apply by: ${formatDate(job.last_date)}</span>
                <span>🎯 Min CGPA: ${job.eligibility_cgpa}</span>
                <span>📚 Max Backlogs: ${job.max_backlogs}</span>
            </div>

            <p style="font-size: 13px; color: #6b7280; margin: 12px 0;">
                <strong>Eligible Branches:</strong> ${job.eligibility_branches}
            </p>

            ${job.is_eligible ?
                `<span class="eligibility-badge eligible">✓ You are eligible</span>` :
                `<span class="eligibility-badge not-eligible">✗ Not eligible</span>`
            }

            ${job.has_applied ?
                '<button class="btn btn-secondary mt-10" disabled>Applied ✓</button>' :
                job.is_eligible ?
                    `<button class="btn btn-primary mt-10" onclick="applyToJob(${job.id}, '${job.company_name}', '${job.job_title}')">Apply Now</button>` :
                    '<button class="btn btn-secondary mt-10" disabled>Not Eligible</button>'
            }
        </div>
    `).join('');
}

// Apply to job
async function applyToJob(jobId, company, title) {
    if (!confirm(`Apply to ${company} for ${title}?\n\nThis action cannot be undone.`)) {
        return;
    }

    try {
        await apiCall(`/jobs/${jobId}/apply`, { method: 'POST' });
        showSuccess('Application submitted successfully!');
        setTimeout(() => window.location.reload(), 1000);
    } catch (error) {
        showError('Application failed: ' + error.message);
    }
}

// Load applications page
async function loadApplicationsPage() {
    try {
        const data = await apiCall('/jobs/applications');
        displayApplications(data.applications);
    } catch (error) {
        showError('Failed to load applications: ' + error.message);
    }
}

// Display applications
function displayApplications(applications) {
    const container = document.getElementById('applications-table');

    if (applications.length === 0) {
        container.innerHTML = `
            <div class="text-center" style="padding: 40px;">
                <p style="color: #6b7280; margin-bottom: 16px;">You haven't applied to any jobs yet</p>
                <a href="jobs.html" class="btn btn-primary">Browse Jobs</a>
            </div>
        `;
        return;
    }

    container.innerHTML = `
        <table>
            <thead>
                <tr>
                    <th>Company</th>
                    <th>Position</th>
                    <th>Salary</th>
                    <th>Applied Date</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
                ${applications.map(app => `
                    <tr>
                        <td><strong>${app.job.company_name}</strong></td>
                        <td>${app.job.job_title}</td>
                        <td>${app.job.salary_package}</td>
                        <td>${formatDate(app.applied_at)}</td>
                        <td><span class="status-badge ${app.status}">${app.status.toUpperCase()}</span></td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;
}

// Load profile page
async function loadProfilePage() {
    try {
        const data = await apiCall('/student/profile');
        displayProfile(data.student);
    } catch (error) {
        showError('Failed to load profile: ' + error.message);
    }
}

// Display profile
function displayProfile(student) {
    document.getElementById('profile-usn').textContent = student.usn;
    document.getElementById('profile-name').value = student.name;
    document.getElementById('profile-email').value = student.email;
    document.getElementById('profile-branch').textContent = student.branch;
    document.getElementById('profile-year').textContent = student.year;
    document.getElementById('profile-cgpa').value = student.cgpa;
    document.getElementById('profile-backlogs').value = student.backlogs;
    document.getElementById('profile-phone').value = student.phone;
    document.getElementById('profile-skills').value = student.skills || '';
}

// Update profile
async function updateProfile() {
    const data = {
        name: document.getElementById('profile-name').value.trim(),
        cgpa: parseFloat(document.getElementById('profile-cgpa').value),
        backlogs: parseInt(document.getElementById('profile-backlogs').value),
        phone: document.getElementById('profile-phone').value.trim(),
        skills: document.getElementById('profile-skills').value.trim()
    };

    if (data.cgpa < 0 || data.cgpa > 10) {
        showError('CGPA must be between 0.0 and 10.0');
        return;
    }

    if (data.backlogs < 0) {
        showError('Backlogs cannot be negative');
        return;
    }

    try {
        await apiCall('/student/profile', {
            method: 'PUT',
            body: JSON.stringify(data)
        });
        showSuccess('Profile updated successfully!');
        setTimeout(() => window.location.reload(), 1500);
    } catch (error) {
        showError('Update failed: ' + error.message);
    }
}
