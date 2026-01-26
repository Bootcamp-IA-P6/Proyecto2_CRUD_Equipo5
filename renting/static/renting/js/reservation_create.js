// renting/static/renting/js/reservation_create.js

function clearReservationErrors() {
    // 1. 개별 필드 에러 지우기
    const form = document.getElementById('res-create-form');
    if (form) {
        form.querySelectorAll('.text-danger').forEach(el => el.textContent = '');
    }    
    // 2. 전역 알림 영역 지우기 (base.html의 컨테이너 접근)
    const container = document.getElementById('global-alert-container');
    if (container) container.innerHTML = '';
}

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

    // UI 상태: 로딩 중
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
        // [FIX] 버튼 상태 복구
        submitBtn.disabled = false;
        submitBtn.textContent = 'Reserve Now';
    }
};

/**
 * 초기화: 차량 목록 로드 및 날짜 제한 설정
 */
async function initReservationPage() {
    // 1. 날짜 제한 (오늘 이전 선택 불가)
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('start_date').setAttribute('min', today);
    document.getElementById('end_date').setAttribute('min', today);

    // 2. 차량 목록 로드
    const carRes = await fetchWithAuth('/api/cars/');
    if (carRes && carRes.ok) {
        const data = await carRes.json();
        const cars = data.results || data;
        const select = document.getElementById('car-select');
        
        select.innerHTML = cars.map(c => 
            `<option value="${c.id}">${c.car_model_name} (${c.license_plate})</option>`
        ).join('');

        // ⚠️ [CORE LOGIC] URL 파라미터 확인 및 자동 선택
        const urlParams = new URLSearchParams(window.location.search);
        const preSelectedCarId = urlParams.get('car');
        
        if (preSelectedCarId) {
            select.value = preSelectedCarId;
            // 시각적 피드백: 테두리 강조
            select.classList.add('border-primary', 'bg-light');
        }
    }
}

document.addEventListener('DOMContentLoaded', initReservationPage);