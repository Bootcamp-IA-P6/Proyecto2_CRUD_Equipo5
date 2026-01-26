// renting/static/renting/js/reservations_history.js

// renting/static/renting/js/reservations_history.js

let currentTab = 'upcoming';

// renting/static/renting/js/reservations_history.js

// ... (currentTab, switchTab 로직 동일)

/**
 * 리스트 렌더링 수정: 카드 클릭 시 상세 드로어 오픈 연결
 */
async function loadMyReservations() {
    const res = await fetchWithAuth(`/api/reservations/my/?status=${currentTab}`);
    if (!res || !res.ok) return;

    const data = await res.json();
    const items = data.results || data;
    const container = document.getElementById('my-res-container');
    
    if (items.length === 0) {
        container.innerHTML = `<div class="text-center py-5 bg-white rounded-4 border border-dashed"><p class="text-muted mb-0">No ${currentTab} reservations found.</p></div>`;
        return;
    }

    container.innerHTML = items.map(r => `
        <div class="res-card" onclick="openReservationDetail(${r.id})" style="cursor: pointer;">
            <div class="res-card-body">
                <div class="res-info-main">
                    <span class="status-badge ${currentTab === 'upcoming' ? 'status-upcoming' : 'status-past'} mb-2 d-inline-block">${currentTab}</span>
                    <h4 class="fw-bold mb-1">${r.model_name.replace('_', ' ')}</h4>
                    <p class="text-muted small mb-0">License: <strong>${r.car_license}</strong></p>
                </div>
                <div class="res-info-date">
                    <div class="small text-muted mb-1">PERIOD</div>
                    <div class="fw-bold text-dark small">${r.start_date} ~ ${r.end_date}</div>
                </div>
                <div class="res-info-price">
                    <div class="fs-5 fw-bold text-primary">${r.total_price}€</div>
                </div>
                <div class="text-muted ms-3"><i class="bi bi-chevron-right"></i></div>
            </div>
        </div>
    `).join('');
}

/**
 * 예약 상세 정보 로드 및 드로어 표시
 */
async function openReservationDetail(id) {
    const drawer = new bootstrap.Offcanvas(document.getElementById('resDetailDrawer'));
    const content = document.getElementById('drawer-content');
    content.innerHTML = '<div class="text-center p-5"><div class="spinner-border text-primary"></div></div>';
    drawer.show();

    const res = await fetchWithAuth(`/api/reservations/${id}/`);
    if (!res.ok) {
        content.innerHTML = '<p class="p-4 text-danger">Failed to load booking details.</p>';
        return;
    }

    const r = await res.json();
    
    // 이미지 파일명 생성 (이전 이슈의 규칙 적용)
    // 참고: car_model_image 필드가 있다면 그걸 쓰고 아니면 야매 생성
    const brandLow = r.brand_name ? r.brand_name.toLowerCase().replace(/\s/g, '_') : 'brand';
    const modelLow = r.model_name.toLowerCase().replace(/\s/g, '_');
    const imageUrl = r.car_model_image || `/static/renting/images/cars/${brandLow}_${modelLow}_1.jpg`;

    content.innerHTML = `
        <div class="p-0">
            <img src="${imageUrl}" class="img-fluid w-100 mb-4" style="height: 220px; object-fit: cover;" 
                 onerror="this.src='/static/renting/images/cars/placeholder.png'">
            
            <div class="px-4 pb-4">
                <div class="mb-4">
                    <h6 class="text-muted text-uppercase small fw-bold mb-1">${r.brand_name || 'Vehicle'}</h6>
                    <h3 class="fw-bold">${r.model_name.replace('_', ' ')}</h3>
                    <span class="badge ${r.start_date >= new Date().toISOString() ? 'bg-success' : 'bg-secondary'} rounded-pill">
                        ${r.start_date >= new Date().toISOString() ? 'Upcoming' : 'Past History'}
                    </span>
                </div>

                <div class="bg-light p-3 rounded-3 mb-4">
                    <div class="d-flex justify-content-between mb-2">
                        <span class="text-muted small">License Plate</span>
                        <span class="fw-bold text-uppercase">${r.car_license}</span>
                    </div>
                    <div class="d-flex justify-content-between mb-2">
                        <span class="text-muted small">Pick-up Date</span>
                        <span class="fw-bold">${r.start_date}</span>
                    </div>
                    <div class="d-flex justify-content-between">
                        <span class="text-muted small">Return Date</span>
                        <span class="fw-bold">${r.end_date}</span>
                    </div>
                </div>

                <div class="d-flex justify-content-between align-items-center mb-5">
                    <span class="h5 mb-0 fw-bold">Total Paid</span>
                    <span class="h3 mb-0 fw-bold text-primary">${r.total_price}€</span>
                </div>

                <!-- ⚠️ 액션 섹션 -->
                ${r.start_date >= new Date().toISOString().split('T')[0] ? `
                    <div class="d-grid gap-2">
                        <button class="btn btn-outline-danger py-3 fw-bold" onclick="openDeleteModal(${r.id})">
                            Cancel Reservation
                        </button>
                    </div>
                ` : `
                    <div class="alert alert-light text-center border-0 small">
                        This is a past reservation and cannot be modified.
                    </div>
                `}
            </div>
        </div>
    `;
}

// ... openDeleteModal 및 final-delete-btn 로직 동일

function switchTab(status, btn) {
    currentTab = status;
    document.querySelectorAll('.res-tab-btn').forEach(el => el.classList.remove('active'));
    btn.classList.add('active');
    loadMyReservations();
}


let targetDeleteId = null;
const delModal = new bootstrap.Modal(document.getElementById('deleteModal'));

function openDeleteModal(id) {
    targetDeleteId = id;
    document.getElementById('delete-confirm-pass').value = '';
    delModal.show();
}



document.getElementById('final-delete-btn').onclick = async () => {
    const passField = document.getElementById('delete-confirm-pass');
    const errorBox = document.getElementById('modal-error-msg');
    const pass = passField.value;

    // 1. 초기화
    errorBox.classList.add('d-none');
    errorBox.innerText = '';

    if (!pass) {
        errorBox.innerText = "Please enter your password.";
        errorBox.classList.remove('d-none');
        return;
    }

    const btn = document.getElementById('final-delete-btn');
    btn.disabled = true;
    btn.innerText = "Processing...";

    try {
        const res = await fetchWithAuth(`/api/reservations/${targetDeleteId}/delete-with-password/`, {
            method: 'DELETE',
            body: JSON.stringify({ password: pass })
        });

        if (res && res.ok) {
            // ✅ 성공
            delModal.hide();
            showGlobalAlert("Reservation cancelled successfully.", "success");
            loadMyReservations();
        } else {
            // ❌ 실패: 비밀번호 오류 등
            const result = await res.json();
            // 백엔드 응답 구조(details 혹은 detail)에 맞춰 메시지 추출
            const msg = (result.details && result.details.detail) || result.detail || result.error || "Invalid password.";
            
            errorBox.innerText = msg;
            errorBox.classList.remove('d-none');
            passField.value = ''; // 비밀번호 창 비우기
        }
    } catch (error) {
        console.error("Delete Error:", error);
        errorBox.innerText = "Server communication error.";
        errorBox.classList.remove('d-none');
    } finally {
        btn.disabled = false;
        btn.innerText = "Confirm Cancellation";
    }
};

document.addEventListener('DOMContentLoaded', loadMyReservations);