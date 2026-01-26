// renting/static/renting/js/profile.js

/**
 * Local alert function for profile-specific notifications
 */
function showLocalAlert(containerId, message, type = 'danger') {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    container.innerHTML = `
        <div class="alert alert-${type} alert-dismissible fade show mb-0" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>
    `;
    
    // Auto-dismiss success messages after 3 seconds
    if (type === 'success') {
        setTimeout(() => {
            container.innerHTML = '';
        }, 3000);
    }
}

/**
 * Toggle profile form between view and edit modes
 */
function toggleEditMode(enable) {
    const inputs = document.querySelectorAll('#profile-form input:not([type="password"])');
    const actions = document.getElementById('edit-actions');
    const editBtn = document.getElementById('edit-mode-btn');

    inputs.forEach(input => {
        // Email typically read-only, but backend allows changes
        if (input.id !== 'prof-email') input.disabled = !enable;
    });

    if (enable) {
        actions.classList.remove('d-none');
        editBtn.classList.add('d-none');
    } else {
        actions.classList.add('d-none');
        editBtn.classList.remove('d-none');
        loadProfileData(); // Restore original data
    }
}

/**
 * Load current user profile data from API
 */
async function loadProfileData() {
    const res = await fetchWithAuth('/api/profile/me/');
    if (res && res.ok) {
        const data = await res.json();
        document.getElementById('prof-fname').value = data.first_name;
        document.getElementById('prof-lname').value = data.last_name;
        document.getElementById('prof-email').value = data.email;
        document.getElementById('prof-bdate').value = data.birth_date;
        document.getElementById('prof-license').value = data.license_number;
    }
}

/**
 * Handle profile update form submission (PATCH request)
 */
document.getElementById('profile-form').onsubmit = async (e) => {
    e.preventDefault();
    const msgContainer = 'profile-msg-container';
    document.getElementById(msgContainer).innerHTML = ''; // Clear previous messages

    const currentPass = document.getElementById('prof-current-pass').value;
    if (!currentPass) {
        showLocalAlert(msgContainer, "Password is required to save changes.");
        return;
    }

    const payload = {
        first_name: document.getElementById('prof-fname').value,
        last_name: document.getElementById('prof-lname').value,
        birth_date: document.getElementById('prof-bdate').value,
        license_number: document.getElementById('prof-license').value,
        current_password: currentPass
    };

    const res = await fetchWithAuth('/api/profile/me/', {
        method: 'PATCH',
        body: JSON.stringify(payload)
    });

    if (res && res.ok) {
        showLocalAlert(msgContainer, "Profile updated successfully!", "success");
        document.getElementById('prof-current-pass').value = '';
        toggleEditMode(false);
        updateSidebar(); 
    } else {
        const err = await Auth.parseError(res);
        // Display server error messages
        showLocalAlert(msgContainer, err.error || "Update failed. Check your password.");
    }
};

/**
 * Handle password change form submission
 */
document.getElementById('change-pass-form').onsubmit = async (e) => {
    e.preventDefault();
    const msgContainer = 'password-msg-container';
    document.getElementById(msgContainer).innerHTML = '';

    const oldP = document.getElementById('pass-old').value;
    const newP = document.getElementById('pass-new').value;
    const confP = document.getElementById('pass-confirm').value;

    if (newP !== confP) {
        showLocalAlert(msgContainer, "New passwords do not match.");
        return;
    }

    const res = await fetchWithAuth('/api/profile/me/change-password/', {
        method: 'POST',
        body: JSON.stringify({ old_password: oldP, new_password: newP })
    });

    if (res && res.ok) {
        showLocalAlert(msgContainer, "Password changed successfully! Redirecting to login...", "success");
        // Logout after 2 seconds
        setTimeout(logout, 2000);
    } else {
        const err = await Auth.parseError(res);
        showLocalAlert(msgContainer, err.error || "Failed to change password. Check your current password.");
    }
};

// Load profile data on page load
document.addEventListener('DOMContentLoaded', loadProfileData);
