// renting/static/renting/js/login.js

function clearLoginErrors() {
    document.querySelectorAll('.text-danger').forEach(el => el.textContent = '');
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

    submitBtn.disabled = true;
    submitBtn.textContent = 'Logging in...';

    try {
        const response = await fetch('/api/token/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (response.ok) {
            const data = await response.json();
            Auth.saveTokens(data);
            window.location.href = "/";
        } else {
            // 👈 중앙 집중식 에러 핸들러 호출
            const errors = await Auth.parseError(response);
            
            if (errors.detail) {
                // 로그인 실패 (ID/PW 틀림 등)
                showGlobalAlert(errors.detail);
            } else {
                // 필드별 유효성 검사 에러 (이메일 누락 등)
                for (const key in errors) {
                    const targetId = (key === 'username') ? 'error-username' : `error-${key}`;
                    const errorEl = document.getElementById(targetId);
                    if (errorEl) {
                        errorEl.textContent = Array.isArray(errors[key]) ? errors[key][0] : errors[key];
                    }
                }
            }
            submitBtn.disabled = false;
            submitBtn.textContent = 'Login';
        }
    } catch (error) {
        console.error("Login Error:", error);
        showGlobalAlert("Failed to connect to the server.");
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