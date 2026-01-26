// renting/static/renting/js/register.js

function clearErrors() {
    const form = document.getElementById('res-create-form');
    if (form) {
        form.querySelectorAll('.text-danger').forEach(el => el.textContent = '');
    }
    document.getElementById('form-status').classList.add('d-none');
}

/**
 * Client-side validation matching SignupSerializer rules
 */
function validateFrontend(data, passConfirm) {
    let isValid = true;

    // Names: letters only
    const nameRegex = /^[a-zA-Z\sáéíóúñÁÉÍÓÚÑ]+$/;
    if (!nameRegex.test(data.first_name)) {
        document.getElementById('error-first_name').innerText = "Names can only contain letters.";
        isValid = false;
    }
    if (!nameRegex.test(data.last_name)) {
        document.getElementById('error-last_name').innerText = "Names can only contain letters.";
        isValid = false;
    }

    // Email format
    const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    if (!emailRegex.test(data.email)) {
        document.getElementById('error-email').innerText = "Please enter a valid email.";
        isValid = false;
    }

    // Password strength
    const passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*(),.?":{}|<>]).{8,}$/;
    if (!passwordRegex.test(data.password)) {
        document.getElementById('error-password').innerText = "Must be 8+ chars, with upper, lower, number, and special char.";
        isValid = false;
    }

    // Password confirm
    if (data.password !== passConfirm) {
        document.getElementById('error-password_confirm').innerText = "Passwords do not match.";
        isValid = false;
    }

    // Age (18+)
    if (data.birth_date) {
        const birth = new Date(data.birth_date);
        const today = new Date();
        let age = today.getFullYear() - birth.getFullYear();
        if (today < new Date(today.getFullYear(), birth.getMonth(), birth.getDate())) age--;
        if (age < 18) {
            document.getElementById('error-birth_date').innerText = "Must be at least 18 years old.";
            isValid = false;
        }
    }

    return isValid;
}

document.getElementById('register-form').onsubmit = async (e) => {
    e.preventDefault();
    clearErrors();

    const payload = {
        first_name: document.getElementById('reg-fname').value,
        last_name: document.getElementById('reg-lname').value,
        email: document.getElementById('reg-email').value,
        password: document.getElementById('reg-pass').value,
        birth_date: document.getElementById('reg-bdate').value,
        license_number: document.getElementById('reg-license').value
    };
    const passConfirm = document.getElementById('reg-pass-confirm').value;

    if (!validateFrontend(payload, passConfirm)) return;

    const btn = document.getElementById('submit-btn');
    btn.disabled = true;

    try {
        const response = await fetch('/api/users/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const result = await response.json();

        if (response.ok) {
            alert("Registration Success!");
            // Redirect to login page
            window.location.href = "/login/"; 
        } else {
            const errors = result.details || result;
            for (const field in errors) {
                const errorDiv = document.getElementById(`error-${field}`);
                if (errorDiv) {
                    errorDiv.innerText = Array.isArray(errors[field]) ? errors[field][0] : errors[field];
                }
            }
            btn.disabled = false;
        }
    } catch (error) {
        console.error(error);
        alert("Server communication error.");
        btn.disabled = false;
    }
};