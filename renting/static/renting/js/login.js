// renting/static/renting/js/login.js

function clearLoginErrors() {
    const form = document.getElementById('res-create-form');
    if (form) {
        form.querySelectorAll('.text-danger').forEach(el => el.textContent = '');
    }    
    const container = document.getElementById('global-alert-container');
    if (container) container.innerHTML = '';
}

document.getElementById('login-form').onsubmit = async (e) => {
    e.preventDefault();
    clearLoginErrors();

    const emailField = document.getElementById('email');
    const passwordField = document.getElementById('password');
    const submitBtn = e.target.querySelector('button[type="submit"]');

    const payload = {
        username: emailField.value.trim(),
        password: passwordField.value
    };

    document.querySelectorAll('.text-danger').forEach(el => el.textContent = '');
    submitBtn.disabled = true;
    submitBtn.textContent = 'Logging in...';

    try {
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;

        const response = await fetch('/api/token/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username: email, password: password })
        });

        const result = await response.json();

        if (response.ok) {
            Auth.saveTokens(result);
            window.location.href = "/";
        } else {
            const errors = result.details || result;
            if (errors.detail) {
                showGlobalAlert(errors.detail);
            } else {
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
        // [FIX] 어떤 경우에도 버튼은 다시 활성화되어야 함
        submitBtn.disabled = false;
        submitBtn.textContent = 'Login';
    }
};

// 세션 만료 등의 메시지 확인
document.addEventListener('DOMContentLoaded', () => {
    const params = new URLSearchParams(window.location.search);
    if (params.get('reason') === 'expired') {
        showGlobalAlert("Your session has expired. Please log in again.", "warning");
    }
});