// Common utilities and API wrapper

const API_BASE_URL = 'http://localhost:5000/api';

/**
 * Make API call with credentials (session cookies)
 */
async function apiCall(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`;

    const defaultOptions = {
        credentials: 'include', // Include cookies for session
        headers: {
            'Content-Type': 'application/json'
        }
    };

    const finalOptions = { ...defaultOptions, ...options };

    // Merge headers
    if (options.headers) {
        finalOptions.headers = { ...defaultOptions.headers, ...options.headers };
    }

    try {
        const response = await fetch(url, finalOptions);

        // Handle 401 Unauthorized - session expired
        if (response.status === 401) {
            // Redirect to login unless already on login page
            if (!window.location.pathname.includes('index.html') &&
                !window.location.pathname.endsWith('/')) {
                alert('Session expired. Please login again.');
                window.location.href = '../index.html';
            }
            throw new Error('Unauthorized');
        }

        // Parse JSON response
        const data = await response.json();

        // Handle non-OK responses
        if (!response.ok) {
            throw new Error(data.error || data.message || 'Request failed');
        }

        return data;

    } catch (error) {
        // Re-throw for caller to handle
        throw error;
    }
}

/**
 * Upload file (multipart/form-data)
 */
async function uploadFile(endpoint, formData) {
    const url = `${API_BASE_URL}${endpoint}`;

    try {
        const response = await fetch(url, {
            method: 'POST',
            credentials: 'include',
            body: formData // Don't set Content-Type for FormData
        });

        if (response.status === 401) {
            alert('Session expired. Please login again.');
            window.location.href = '../index.html';
            throw new Error('Unauthorized');
        }

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'Upload failed');
        }

        return data;

    } catch (error) {
        throw error;
    }
}

/**
 * Check if user is authenticated
 */
async function checkSession() {
    try {
        const data = await apiCall('/auth/session');
        return data.authenticated ? data.user : null;
    } catch (error) {
        return null;
    }
}

/**
 * Show error message
 */
function showError(message, containerId = 'error-container') {
    const container = document.getElementById(containerId);
    if (container) {
        container.innerHTML = `
            <div class="alert alert-error">
                ${message}
            </div>
        `;
        container.style.display = 'block';
    } else {
        alert(message);
    }
}

/**
 * Show success message
 */
function showSuccess(message, containerId = 'success-container') {
    const container = document.getElementById(containerId);
    if (container) {
        container.innerHTML = `
            <div class="alert alert-success">
                ${message}
            </div>
        `;
        container.style.display = 'block';

        // Auto-hide after 3 seconds
        setTimeout(() => {
            container.style.display = 'none';
        }, 3000);
    }
}

/**
 * Clear messages
 */
function clearMessages() {
    const errorContainer = document.getElementById('error-container');
    const successContainer = document.getElementById('success-container');

    if (errorContainer) errorContainer.style.display = 'none';
    if (successContainer) successContainer.style.display = 'none';
}

/**
 * Show loading state on button
 */
function setButtonLoading(buttonId, loading, loadingText = 'Loading...') {
    const button = document.getElementById(buttonId);
    if (button) {
        button.disabled = loading;
        if (loading) {
            button.setAttribute('data-original-text', button.textContent);
            button.textContent = loadingText;
        } else {
            const originalText = button.getAttribute('data-original-text');
            if (originalText) {
                button.textContent = originalText;
            }
        }
    }
}

/**
 * Format date to readable string
 */
function formatDate(dateString) {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-IN', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

/**
 * Format datetime to readable string
 */
function formatDateTime(dateString) {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleString('en-IN', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

/**
 * Calculate time remaining
 */
function getTimeRemaining(endTime) {
    const now = new Date().getTime();
    const end = new Date(endTime).getTime();
    const diff = end - now;

    if (diff <= 0) {
        return { total: 0, minutes: 0, seconds: 0 };
    }

    return {
        total: diff,
        minutes: Math.floor((diff / 1000 / 60) % 60),
        seconds: Math.floor((diff / 1000) % 60)
    };
}

/**
 * Logout user
 */
async function logout() {
    try {
        await apiCall('/auth/logout', { method: 'POST' });
        window.location.href = window.location.pathname.includes('student/') ||
                              window.location.pathname.includes('admin/')
                              ? '../index.html'
                              : 'index.html';
    } catch (error) {
        alert('Logout failed. Please try again.');
    }
}
