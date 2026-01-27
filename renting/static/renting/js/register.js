// renting/static/renting/js/register.js

/**
 * Clear all form errors and status messages
 */
function clearErrors() {
    const form = document.getElementById('register-form');
    if (form) {
        form.querySelectorAll('.text-danger').forEach(el => el.textContent = '');
    }
    const status = document.getElementById('form-status');
    if (status) status.classList.add('d-none');
}

/**
 * Client-side validation matching SignupSerializer backend rules
 */
function validateFrontend(data, passConfirm) {
    let isValid = true;

    // Names: letters only (matches backend regex)
    const nameRegex = /^[a-zA-Z\sáéíóúñÁÉÍÓÚÑ]+$/;
    if (!data.first_name || !nameRegex.test(data.first_name)) {
        document.getElementById('error-first_name').innerText = "Names can only contain letters.";
        isValid = false;
    }
    if (!data.last_name || !nameRegex.test(data.last_name)) {
        document.getElementById('error-last_name').innerText = "Names can only contain letters.";
        isValid = false;
    }

    // Email format validation
    const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    if (!emailRegex.test(data.email)) {
        document.getElementById('error-email').innerText = "Please enter a valid email.";
        isValid = false;
    }

    // Password strength (8+ chars, upper, lower, number, special)
    const passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*(),.?":{}|<>]).{8,}$/;
    if (!passwordRegex.test(data.password)) {
        document.getElementById('error-password').innerText = "Must be 8+ chars, with upper, lower, number, and special char.";
        isValid = false;
    }

    // Password confirmation match
    if (data.password !== passConfirm) {
        document.getElementById('error-password_confirm').innerText = "Passwords do not match.";
        isValid = false;
    }

    // Age validation (18+ years)
    if (!data.birth_date) {
        document.getElementById('error-birth_date').innerText = "Birth date is required.";
        isValid = false;
    } else {
        const birth = new Date(data.birth_date);
        const today = new Date();
        let age = today.getFullYear() - birth.getFullYear();
        if (today < new Date(today.getFullYear(), birth.getMonth(), birth.getDate())) age--;
        if (age < 18) {
            document.getElementById('error-birth_date').innerText = "You must be at least 18 years old.";
            isValid = false;
        }
    }

    return isValid;
}

/**
 * Handle registration form submission
 */
document.getElementById('register-form').onsubmit = async (e) => {
    e.preventDefault();
    clearErrors();

    // Collect form data
    const payload = {
        first_name: document.getElementById('reg-fname').value,
        last_name: document.getElementById('reg-lname').value,
        email: document.getElementById('reg-email').value,
        password: document.getElementById('reg-pass').value,
        birth_date: document.getElementById('reg-bdate').value,
        license_number: document.getElementById('reg-license').value.trim()
    };
    const passConfirm = document.getElementById('reg-pass-confirm').value;

    // Frontend validation before API call
    if (!validateFrontend(payload, passConfirm)) return;

    const btn = document.getElementById('submit-btn');
    const originalBtnText = btn.textContent;
    btn.disabled = true;
    btn.textContent = "Creating Account...";

    try {
        // Submit to user creation API endpoint
        const response = await fetch('/api/users/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const result = await response.json();

        if (response.ok) {
            // Redirect to login page
            if (window.redirectWithMsg) {
                window.redirectWithMsg("/login/", "Account created successfully! Please sign in.", "success");
            } else {
                window.location.href = "/login/";
            }
        } else {
            // Display backend validation errors
            const errors = result.details || result;
            for (const field in errors) {
                const errorDiv = document.getElementById(`error-${field}`);
                if (errorDiv) {
                    errorDiv.innerText = Array.isArray(errors[field]) ? errors[field][0] : errors[field];
                }
            }
            btn.disabled = false;
            btn.textContent = originalBtnText;
        }
    } catch (error) {
        console.error(error);
        const status = document.getElementById('form-status');
        status.innerText = "Connection error. Please try again.";
        status.classList.remove('d-none', 'alert-success');
        status.classList.add('alert-danger');
        btn.disabled = false;
        btn.textContent = originalBtnText;
    }
};
