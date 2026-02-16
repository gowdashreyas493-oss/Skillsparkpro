#!/bin/bash

# Create admin pages with templates

# Admin Dashboard
cat > frontend/admin/dashboard.html << 'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin Dashboard - SkillSpark Pro</title>
    <link rel="stylesheet" href="../css/styles.css">
</head>
<body>
    <div class="dashboard-container">
        <aside class="sidebar">
            <div class="sidebar-header">
                <h2>SkillSpark Pro</h2>
                <p>Admin Portal</p>
            </div>
            <nav class="sidebar-nav">
                <a href="dashboard.html" class="nav-item active">Dashboard</a>
                <a href="students.html" class="nav-item">Manage Students</a>
                <a href="create-job.html" class="nav-item">Create Job</a>
                <a href="applications.html" class="nav-item">Applications</a>
                <a href="create-exam.html" class="nav-item">Create Exam</a>
            </nav>
        </aside>
        <main class="main-content">
            <div class="top-bar">
                <div class="user-info">
                    <div class="user-details">
                        <div class="name" id="user-name">Admin</div>
                        <div class="meta">Administrator</div>
                    </div>
                </div>
                <button class="logout-btn" onclick="logout()">Logout</button>
            </div>
            <div class="content-wrapper">
                <div class="page-header">
                    <h1>Admin Dashboard</h1>
                    <p>System Overview</p>
                </div>
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="label">Total Students</div>
                        <div class="value" id="stat-students">-</div>
                    </div>
                    <div class="stat-card">
                        <div class="label">Active Jobs</div>
                        <div class="value" id="stat-jobs">-</div>
                    </div>
                    <div class="stat-card">
                        <div class="label">Total Exams</div>
                        <div class="value" id="stat-exams">-</div>
                    </div>
                    <div class="stat-card">
                        <div class="label">Applications</div>
                        <div class="value" id="stat-applications">-</div>
                    </div>
                </div>
                <div class="card">
                    <div class="card-header"><h2>Recent Activity</h2></div>
                    <div class="card-body" id="recent-activity"><div class="spinner"></div></div>
                </div>
            </div>
        </main>
    </div>
    <script src="../js/common.js"></script>
    <script src="../js/admin.js"></script>
    <script>
        document.addEventListener('DOMContentLoaded', async () => {
            const user = await checkSession();
            if (!user || user.role !== 'admin') {
                window.location.href = '../index.html';
                return;
            }
            document.getElementById('user-name').textContent = user.name;
            await loadAdminDashboard();
        });
    </script>
</body>
</html>
EOF

# Admin Students Page
cat > frontend/admin/students.html << 'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Students - SkillSpark Pro</title>
    <link rel="stylesheet" href="../css/styles.css">
</head>
<body>
    <div class="dashboard-container">
        <aside class="sidebar">
            <div class="sidebar-header">
                <h2>SkillSpark Pro</h2>
                <p>Admin Portal</p>
            </div>
            <nav class="sidebar-nav">
                <a href="dashboard.html" class="nav-item">Dashboard</a>
                <a href="students.html" class="nav-item active">Manage Students</a>
                <a href="create-job.html" class="nav-item">Create Job</a>
                <a href="applications.html" class="nav-item">Applications</a>
                <a href="create-exam.html" class="nav-item">Create Exam</a>
            </nav>
        </aside>
        <main class="main-content">
            <div class="top-bar">
                <div class="user-info"><div class="user-details"><div class="name">Admin</div></div></div>
                <button class="logout-btn" onclick="logout()">Logout</button>
            </div>
            <div class="content-wrapper">
                <div class="page-header">
                    <h1>Manage Students</h1>
                    <p>View all registered students</p>
                </div>
                <div class="card">
                    <div class="card-body" id="students-table"><div class="spinner"></div></div>
                </div>
            </div>
        </main>
    </div>
    <script src="../js/common.js"></script>
    <script src="../js/admin.js"></script>
    <script>
        document.addEventListener('DOMContentLoaded', async () => {
            const user = await checkSession();
            if (!user || user.role !== 'admin') {
                window.location.href = '../index.html';
                return;
            }
            await loadStudentsPage();
        });
    </script>
</body>
</html>
EOF

# Create course directories and index pages
mkdir -p frontend/courses/{1,2,3,4,5,6}

for i in {1..6}; do
    cat > frontend/courses/$i/index.html << EOF
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Course $i - SkillSpark Pro</title>
    <link rel="stylesheet" href="../../css/styles.css">
</head>
<body>
    <div class="dashboard-container">
        <main class="main-content" style="margin-left: 0;">
            <div class="top-bar">
                <div class="user-info">
                    <h2>Course Content</h2>
                </div>
                <button class="btn btn-secondary" onclick="window.location.href='../../student/courses.html'">Back to Courses</button>
            </div>
            <div class="content-wrapper">
                <div class="page-header">
                    <h1>Course Module</h1>
                    <p>Learning content will be available here</p>
                </div>
                <div class="card">
                    <div class="card-body">
                        <p>Course content is being developed. Check back soon!</p>
                        <button class="btn btn-primary mt-20" onclick="markProgress()">Mark as Complete</button>
                    </div>
                </div>
            </div>
        </main>
    </div>
    <script src="../../js/common.js"></script>
    <script>
        async function markProgress() {
            try {
                await apiCall('/student/courses/$i/progress', {
                    method: 'PUT',
                    body: JSON.stringify({ progress_percentage: 100 })
                });
                alert('Progress updated!');
                window.location.href = '../../student/courses.html';
            } catch (error) {
                alert('Failed to update progress: ' + error.message);
            }
        }
    </script>
</body>
</html>
EOF
done

echo "✓ All remaining files created successfully!"
echo "✓ Admin pages: dashboard.html, students.html"
echo "✓ Course content pages: 6 directories with index.html"

