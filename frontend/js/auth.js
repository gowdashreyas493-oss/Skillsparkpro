// Authentication logic

// Tab switching
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

    const usn = document.getElementById('login-usn').value.trim();
    const password = document.getElementById('login-password').value;

    if (!usn || !password) {
        showError('Please enter both USN and password');
        return;
    }

    setButtonLoading('login-btn', true, 'Logging in...');

    try {
        const data = await apiCall('/auth/login', {
            method: 'POST',
            body: JSON.stringify({ usn, password })
        });

        // Redirect based on role
        if (data.user.role === 'student') {
            window.location.href = 'student/dashboard.html';
        } else if (data.user.role === 'admin') {
            window.location.href = 'admin/dashboard.html';
        }

    } catch (error) {
        showError(error.message || 'Login failed. Please check your credentials.');
        setButtonLoading('login-btn', false);
    }
});

// Handle registration
document.getElementById('register-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    clearMessages();

    const usn = document.getElementById('register-usn').value.trim();
    const name = document.getElementById('register-name').value.trim();
    const email = document.getElementById('register-email').value.trim();
    const password = document.getElementById('register-password').value;
    const branch = document.getElementById('register-branch').value;
    const year = parseInt(document.getElementById('register-year').value);
    const cgpa = parseFloat(document.getElementById('register-cgpa').value);
    const phone = document.getElementById('register-phone').value.trim();

    // Validation
    if (usn.length !== 10) {
        showError('USN must be exactly 10 characters');
        return;
    }

    if (password.length < 6) {
        showError('Password must be at least 6 characters');
        return;
    }

    if (cgpa < 0 || cgpa > 10) {
        showError('CGPA must be between 0.0 and 10.0');
        return;
    }

    if (phone.length !== 10 || !/^\d+$/.test(phone)) {
        showError('Phone number must be exactly 10 digits');
        return;
    }

    const data = {
        usn,
        name,
        email,
        password,
        branch,
        year,
        cgpa,
        phone
    };

    setButtonLoading('register-btn', true, 'Registering...');

    try {
        await apiCall('/auth/register', {
            method: 'POST',
            body: JSON.stringify(data)
        });

        // Auto-login after successful registration (student)
        window.location.href = 'student/dashboard.html';

    } catch (error) {
        showError(error.message || 'Registration failed. Please try again.');
        setButtonLoading('register-btn', false);
    }
});
