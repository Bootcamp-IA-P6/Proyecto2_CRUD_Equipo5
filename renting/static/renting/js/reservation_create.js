// renting/static/renting/js/reservation_create.js

/**
 * Clear all reservation form errors and global alerts
 */
function clearReservationErrors() {
    // 1. Clear individual field errors
    const form = document.getElementById('res-create-form');
    if (form) {
        form.querySelectorAll('.text-danger').forEach(el => el.textContent = '');
    }     
    // 2. Clear global alert container (from base.html)
    const container = document.getElementById('global-alert-container');
    if (container) container.innerHTML = '';
}

/**
 * Handle reservation form submission
 */
document.getElementById('res-create-form').onsubmit = async (e) => {
    e.preventDefault();
    clearReservationErrors();

    const submitBtn = e.target.querySelector('button[type="submit"]');
    const carField = document.getElementById('car-select');
    const startField = document.getElementById('start_date');
    const endField = document.getElementById('end_date');

    const payload = {
        car: carField.value,
        start_date: startField.value,
        end_date: endField.value
    };

    // Set UI loading state
    submitBtn.disabled = true;
    submitBtn.textContent = 'Processing...';

    try {
        const payload = {
            car: document.getElementById('car-select').value,
            start_date: document.getElementById('start_date').value,
            end_date: document.getElementById('end_date').value
        };

        const response = await fetchWithAuth('/api/reservations/', {
            method: 'POST',
            body: JSON.stringify(payload)
        });

        if (response && response.ok) {
            window.location.href = "/reservations/?msg=success";
        } else {
            const errors = await Auth.parseError(response);
            const globalMsg = errors.detail || 
                    (errors.non_field_errors ? errors.non_field_errors[0] : null) ||
                    (errors.__all__ ? errors.__all__[0] : null);

            if (globalMsg) showGlobalAlert(globalMsg);

            for (const key in errors) {
                if (['detail', 'non_field_errors', '__all__'].includes(key)) continue;
                const errorEl = document.getElementById(`error-${key}`);
                if (errorEl) errorEl.textContent = Array.isArray(errors[key]) ? errors[key][0] : errors[key];
            }
        }
    } catch (error) {
        console.error("Reservation Error:", error);
        showGlobalAlert("Failed to connect to the server.");
    } finally {
        // Always restore button state
        submitBtn.disabled = false;
        submitBtn.textContent = 'Reserve Now';
    }
};

/**
 * Initialize reservation page: load cars and set date restrictions
 */
async function initReservationPage() {
    // 1. Set date restrictions (no past dates)
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('start_date').setAttribute('min', today);
    document.getElementById('end_date').setAttribute('min', today);

    // 2. Load available cars list
    const carRes = await fetchWithAuth('/api/cars/');
    if (carRes && carRes.ok) {
        const data = await carRes.json();
        const cars = data.results || data;
        const select = document.getElementById('car-select');
        
        select.innerHTML = cars.map(c => 
            `<option value="${c.id}">${c.car_model_name} (${c.license_plate})</option>`
        ).join('');

        // CORE LOGIC: Check URL params and auto-select car
        const urlParams = new URLSearchParams(window.location.search);
        const preSelectedCarId = urlParams.get('car');
        
        if (preSelectedCarId) {
            select.value = preSelectedCarId;
            // Visual feedback: highlight border
            select.classList.add('border-primary', 'bg-light');
        }
    }
}

// Initialize page on DOM load
document.addEventListener('DOMContentLoaded', initReservationPage);
