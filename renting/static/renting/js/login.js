// renting/static/renting/js/login.js

function clearLoginErrors() {
    document.querySelectorAll('.text-danger').forEach(el => el.textContent = '');
    const globalError = document.getElementById('global-error');
    globalError.classList.add('d-none');
    globalError.textContent = '';
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

        const result = await response.json();

        if (response.ok) {
            Auth.saveTokens(result);
            window.location.href = "/";
        } else {
            // ⚠️ 핵심 수정: 커스텀 핸들러의 "details" 키 또는 "detail" 메시지 대응
            const errors = result.details || result;

            if (errors.detail) {
                // 전체 에러 메시지 (로그인 실패 등)
                const globalError = document.getElementById('global-error');
                globalError.textContent = errors.detail;
                globalError.classList.remove('d-none');
            } else {
                // 필드별 에러 메시지 (Email 필수 등)
                for (const key in errors) {
                    // 키값이 username이면 email 필드 아래에 표시 (우리 모델의 특징)
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
        console.error("Login Fetch Error:", error);
        const globalError = document.getElementById('global-error');
        globalError.textContent = "Server connection error.";
        globalError.classList.remove('d-none');
        submitBtn.disabled = false;
        submitBtn.textContent = 'Login';
    }
};

// 세션 만료 등의 이유로 넘어왔을 때 표시
document.addEventListener('DOMContentLoaded', () => {
    const params = new URLSearchParams(window.location.search);
    if (params.get('reason') === 'expired') {
        const globalError = document.getElementById('global-error');
        globalError.textContent = "Your session has expired. Please login again.";
        globalError.classList.remove('d-none');
        globalError.className = "alert alert-warning mb-3";
    }
});