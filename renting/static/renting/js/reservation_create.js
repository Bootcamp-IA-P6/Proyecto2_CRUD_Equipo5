// renting/static/renting/js/reservation_create.js

function clearReservationErrors() {
    // 1. 개별 필드 에러 지우기
    document.querySelectorAll('.text-danger').forEach(el => el.textContent = '');
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
        const response = await fetchWithAuth('/api/reservations/', {
            method: 'POST',
            body: JSON.stringify(payload)
        });

        if (response && response.ok) {
            // ✅ 성공: 팝업 없이 즉시 목록으로 이동 (URL 파라미터로 성공 메시지 전달 가능)
            window.location.href = "/reservations/?msg=created";
        } else {
            // ❌ 실패: 이슈 #49의 중앙 집중식 에러 파서 사용
            const errors = await Auth.parseError(response);
            
            // 1) 기술적 에러 (__all__, non_field_errors) 또는 상세 메시지(detail) 처리
            const globalMsg = errors.detail || 
                            (errors.non_field_errors ? errors.non_field_errors[0] : null) ||
                            (errors.__all__ ? errors.__all__[0] : null);

            if (globalMsg) {
                // base.html의 전역 알림 함수 호출
                showGlobalAlert(globalMsg);
            } 
            
            // 2) 개별 필드 에러 (car, start_date, end_date) 매핑
            for (const key in errors) {
                if (key === 'non_field_errors' || key === '__all__' || key === 'detail') continue;
                
                const errorEl = document.getElementById(`error-${key}`);
                if (errorEl) {
                    errorEl.textContent = Array.isArray(errors[key]) ? errors[key][0] : errors[key];
                }
            }
            
            submitBtn.disabled = false;
            submitBtn.textContent = 'Reserve Now';
        }
    } catch (error) {
        console.error("Reservation Error:", error);
        showGlobalAlert("Failed to connect to the server.");
        submitBtn.disabled = false;
        submitBtn.textContent = 'Reserve Now';
    }
};

/**
 * 초기화: 차량 목록 로드 및 날짜 제한 설정
 */
async function initReservationPage() {
    // 오늘 이전 날짜 선택 방지
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

document.addEventListener('DOMContentLoaded', initReservationPage);