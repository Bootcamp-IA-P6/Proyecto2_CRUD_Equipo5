// renting/static/renting/js/home.js

let nextPageUrl = '/api/cars/';
let isLoading = false;

async function loadVehicleTypes() {
    const res = await fetch('/api/vehicle-types/');
    if (res.ok) {
        const data = await res.json();
        const types = data.results || data;
        const select = document.getElementById('filter-type');
        // 기존 옵션 유지하고 추가
        let options = '<option value="">All Types</option>';
        types.forEach(t => {
            options += `<option value="${t.id}">${t.name}</option>`;
        });
        select.innerHTML = options;
    }
}

async function loadVehicles(reset = false) {
    if (isLoading || (!nextPageUrl && !reset)) return;
    
    isLoading = true;
    toggleUIState(true); // 로딩 UI 켜기

    if (reset) {
        const search = document.getElementById('search-input').value;
        const type = document.getElementById('filter-type').value;
        nextPageUrl = `/api/cars/?search=${search}&car_model__vehicle_type=${type}`;
        document.getElementById('vehicle-list').innerHTML = '';
    }
    
    try {
        const response = await fetchWithAuth(nextPageUrl);
        if (!response) throw new Error("Auth failed");

        const data = await response.json();
        const items = data.results || [];
        nextPageUrl = data.next;

        renderCards(items);
    } catch (e) {
        console.error("Load failed:", e);
    } finally {
        isLoading = false;
        toggleUIState(false); // 로딩 UI 끄기
    }
}

/**
 * 카드 렌더링
 */
function renderCards(items) {
    const grid = document.getElementById('vehicle-list');
    items.forEach(c => {
        const card = document.createElement('div');
        card.className = 'vehicle-card';
        card.innerHTML = `
            <div class="card-img-wrapper">
                <img src="${c.car_model_image || '/static/renting/images/cars/placeholder.png'}" alt="${c.car_model_name}">
            </div>
            <div class="card-info">
                <div class="d-flex justify-content-between align-items-start mb-2">
                    <div>
                        <span class="text-muted small text-uppercase fw-bold">${c.brand_name}</span>
                        <h5 class="mb-0">${c.car_model_name}</h5>
                    </div>
                    <span class="badge bg-light text-dark border">${c.color_name}</span>
                </div>
                <hr>
                <div class="d-flex justify-content-between align-items-center">
                    <span class="price-tag">${c.daily_price || '0'}€ <small class="text-muted fw-normal" style="font-size: 0.7rem;">/day</small></span>
                    <a href="/reservations/create/?car=${c.id}" class="btn btn-accent btn-sm px-3">Book Now</a>
                </div>
            </div>
        `;
        grid.appendChild(card);
    });
}


/**
 * 상태에 따른 버튼/스피너 제어
 */
function toggleUIState(loading) {
    const btn = document.getElementById('load-more-btn');
    const spinner = document.getElementById('loading-spinner');
    const msg = document.getElementById('no-more-msg');

    if (loading) {
        spinner.classList.remove('d-none');
        btn.classList.add('d-none');
    } else {
        spinner.classList.add('d-none');
        if (nextPageUrl) {
            btn.classList.remove('d-none'); // 다음 데이터가 있으면 버튼 노출
        } else {
            btn.classList.add('d-none');
            if (document.getElementById('vehicle-list').children.length > 0) {
                msg.classList.remove('d-none'); // 진짜 끝이면 메시지 노출
            }
        }
    }
}


/**
 * ⚠️ 무한 스크롤 옵저버 (Intersection Observer)
 */
const observer = new IntersectionObserver((entries) => {
    // 센서가 화면에 보이고, 현재 로딩 중이 아니며, 다음 페이지가 있을 때만 실행
    if (entries[0].isIntersecting && !isLoading && nextPageUrl) {
        console.log("Automatic load triggered by scroll...");
        loadVehicles();
    }
}, { threshold: 0.1 });

document.addEventListener('DOMContentLoaded', () => {
    loadVehicleTypes();
    loadVehicles();
    
    // 바닥 감지 시작
    const sentinel = document.getElementById('scroll-sentinel');
    if (sentinel) observer.observe(sentinel);
});


document.addEventListener('DOMContentLoaded', () => {
    loadVehicleTypes();
    loadVehicles();
});