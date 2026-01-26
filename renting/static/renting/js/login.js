// renting/static/renting/js/login.js

/**
 * Clear all login error messages and global alerts
 */
function clearLoginErrors() {
    const form = document.getElementById('res-create-form');
    if (form) {
        form.querySelectorAll('.text-danger').forEach(el => el.textContent = '');
    }     
    const container = document.getElementById('global-alert-container');
    if (container) container.innerHTML = '';
}

/**
 * Handle login form submission with API authentication
 */
document.getElementById('login-form').onsubmit = async (e) => {
    e.preventDefault();
    clearLoginErrors();

    // Get form fields and submit button
    const emailField = document.getElementById('email');
    const passwordField = document.getElementById('password');
    const submitBtn = e.target.querySelector('button[type="submit"]');

    // Prepare payload for JWT token request
    const payload = {
        username: emailField.value.trim(),
        password: passwordField.value
    };

    // Clear previous errors and show loading state
    document.querySelectorAll('.text-danger').forEach(el => el.textContent = '');
    submitBtn.disabled = true;
    submitBtn.textContent = 'Logging in...';

    try {
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;

        // Call JWT token endpoint
        const response = await fetch('/api/token/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username: email, password: password })
        });

        const result = await response.json();

        if (response.ok) {
            // Save tokens and redirect to home
            Auth.saveTokens(result);
            window.location.href = "/";
        } else {
            // Handle server validation errors
            const errors = result.details || result;
            if (errors.detail) {
                showGlobalAlert(errors.detail);
            } else {
                // Display field-specific errors
                for (const key in errors) {
                    const targetId = (key === 'username') ? 'error-username' : `error-${key}`;
                    const errorEl = document.getElementById(targetId);
                    if (errorEl) errorEl.textContent = Array.isArray(errors[key]) ? errors[key][0] : errors[key];
                }
            }
        }
    } catch (error) {
        console.error("Login Error:", error);
        showGlobalAlert("Server connection failed.");
    } finally {
        // Always restore button state
        submitBtn.disabled = false;
        submitBtn.textContent = 'Login';
    }
};

/**
 * Check URL parameters for session expiration messages on page load
 */
document.addEventListener('DOMContentLoaded', () => {
    const params = new URLSearchParams(window.location.search);
    if (params.get('reason') === 'expired') {
        showGlobalAlert("Your session has expired. Please log in again.", "warning");
    }
});
