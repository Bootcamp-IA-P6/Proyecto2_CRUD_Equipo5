// renting/static/renting/js/reservation_create.js

function clearErrors() {
    document.querySelectorAll('.text-danger').forEach(el => el.textContent = '');
    const globalError = document.getElementById('global-error');
    globalError.classList.add('d-none');
}

/**
 * Validates dates on the client side before sending to server
 */
function validateDates(startDate, endDate) {
    const today = new Date().toISOString().split('T')[0];
    let isValid = true;

    if (startDate < today) {
        document.getElementById('error-start_date').textContent = "Start date cannot be in the past.";
        isValid = false;
    }

    if (endDate < startDate) {
        document.getElementById('error-end_date').textContent = "End date must be after or equal to start date.";
        isValid = false;
    }

    return isValid;
}

document.getElementById('res-create-form').onsubmit = async (e) => {
    e.preventDefault();
    clearErrors();

    const submitBtn = e.target.querySelector('button[type="submit"]');
    const payload = {
        car: document.getElementById('car-select').value,
        start_date: document.getElementById('start_date').value,
        end_date: document.getElementById('end_date').value
    };

    // 1. Frontend Validation
    if (!validateDates(payload.start_date, payload.end_date)) return;

    // UI Loading state
    submitBtn.disabled = true;
    submitBtn.textContent = 'Processing...';

    try {
        const response = await fetchWithAuth('/api/reservations/', {
            method: 'POST',
            body: JSON.stringify(payload)
        });

        const result = await response.json();

        if (response && response.ok) {
            alert("Reservation confirmed!");
            window.location.href = "/reservations/";
// renting/static/renting/js/reservation_create.js 내의 에러 처리 로직 부분

} else {
    // 2. Handle Backend Errors (Parsing the 'details' layer)
    const errors = result.details || result;
    
    if (typeof errors === 'string') {
        const globalError = document.getElementById('global-error');
        globalError.textContent = errors;
        globalError.classList.remove('d-none');
    } else {
        for (const key in errors) {
            const errorMessage = Array.isArray(errors[key]) ? errors[key][0] : errors[key];

            // ⚠️ [핵심 수정] 기술적인 키값(__all__, non_field_errors) 처리
            if (key === '__all__' || key === 'non_field_errors') {
                const globalError = document.getElementById('global-error');
                // "__all__:" 접두사 없이 깔끔하게 메시지만 출력
                globalError.textContent = errorMessage; 
                globalError.classList.remove('d-none');
            } else {
                // 특정 필드 에러 (car, start_date 등) 처리
                const errorEl = document.getElementById(`error-${key}`);
                if (errorEl) {
                    errorEl.textContent = errorMessage;
                } else {
                    // 필드 ID를 못 찾은 경우에도 글로벌 에러 박스에 표시 (키 생략)
                    const globalError = document.getElementById('global-error');
                    globalError.textContent = errorMessage;
                    globalError.classList.remove('d-none');
                }
            }
        }
    }
    submitBtn.disabled = false;
    submitBtn.textContent = 'Reserve Now';
}
    } catch (error) {
        console.error("Reservation Error:", error);
        submitBtn.disabled = false;
        submitBtn.textContent = 'Reserve Now';
    }
};

/**
 * Initialize page: Load cars and set min date to today
 */
async function initPage() {
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('start_date').setAttribute('min', today);
    document.getElementById('end_date').setAttribute('min', today);

    const carRes = await fetchWithAuth('/api/cars/');
    if (carRes && carRes.ok) {
        const data = await carRes.json();
        const cars = data.results || data;
        const select = document.getElementById('car-select');
        select.innerHTML = cars.map(c => 
            `<option value="${c.id}">${c.car_model_name} (${c.license_plate})</option>`
        ).join('');
    }
}

document.addEventListener('DOMContentLoaded', initPage);