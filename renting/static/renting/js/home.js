// renting/static/renting/js/home.js

let nextPageUrl = '/api/cars/';
let isLoading = false;

/**
 * UI 입력값을 읽어 API 쿼리 스트링 생성
 */
function getFilterParams() {
    const params = new URLSearchParams();
    
    // Basic search and sorting
    const search = document.getElementById('search-input').value;
    const sort = document.getElementById('sort-order').value;
    if (search) params.append('search', search);
    if (sort) params.append('ordering', sort);

    // Date availability filters
    const from = document.getElementById('available-from').value;
    const to = document.getElementById('available-to').value;
    if (from) params.append('available_from', from);
    if (to) params.append('available_to', to);

    // Detailed spec filters
    const type = document.getElementById('filter-type').value;
    const trans = document.getElementById('filter-trans').value;
    const seats = document.getElementById('filter-seats').value;

    if (type) params.append('car_model__vehicle_type', type);
    if (trans) params.append('transmission', trans);
    if (seats) params.append('seats', seats); 

    return params.toString();
}

async function loadVehicles(reset = false) {
    if (isLoading || (!nextPageUrl && !reset)) return;
    
    isLoading = true;
    toggleUIState(true);

    if (reset) {
        const queryString = getFilterParams();
        nextPageUrl = `/api/cars/?${queryString}`;
        document.getElementById('vehicle-list').innerHTML = '';
    }
    
    try {
        const response = await fetchWithAuth(nextPageUrl);
        if (!response) throw new Error("Auth failed");

        const data = await response.json();
        // Pagination 결과(results) 혹은 일반 배열 대응
        const items = data.results || data;
        nextPageUrl = data.next;

        renderCards(items);
    } catch (e) {
        console.error("Load failed:", e);
    } finally {
        isLoading = false;
        toggleUIState(false);
    }
}

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

/**
 * Render vehicle cards
 */
function renderCards(items) {
    const grid = document.getElementById('vehicle-list');
    items.forEach(c => {
        const div = document.createElement('div');
        div.className = 'vehicle-card'; // CSS 클래스명 유지
        div.innerHTML = `
            <a href="/cars/${c.id}/" class="text-decoration-none">
                <div class="card-img-wrapper">
                    <img src="${c.car_model_image || '/static/renting/images/cars/placeholder.png'}" alt="${c.car_model_name}">
                </div>
            </a>
            <div class="card-info p-3">
                <div class="mb-2">
                    <span class="text-muted small text-uppercase fw-bold">${c.brand_name || 'Brand'}</span>
                    <h5 class="mb-0 text-dark fw-bold">${c.car_model_name}</h5>
                </div>
                <p class="text-muted small mb-2">${c.license_plate} | ${c.mileage ? c.mileage.toLocaleString() : 0} km</p>
                <hr>
                <div class="d-flex justify-content-between align-items-center">
                    <span class="price-tag fw-bold text-primary fs-5">${c.daily_price || '0'}€ <small class="text-muted fw-normal" style="font-size: 0.7rem;">/day</small></span>
                    <a href="/reservations/create/?car=${c.id}" class="btn btn-accent btn-sm px-3">Book Now</a>
                </div>
            </div>
        `;
        grid.appendChild(div);
    });
}

/**
 * Control buttons/spinner state based on loading status
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
            btn.classList.remove('d-none'); // Show button if more data available
        } else {
            btn.classList.add('d-none');
            if (document.getElementById('vehicle-list').children.length > 0) {
                msg.classList.remove('d-none'); // Show end message
            }
        }
    }
}

/**
 * 필터 초기화
 */
function clearAllFilters() {
    document.querySelectorAll('.form-control, .form-select').forEach(el => el.value = '');
    loadVehicles(true);
}


/**
 * Infinite scroll observer (Intersection Observer)
 */
const observer = new IntersectionObserver((entries) => {
    // Execute only when sentinel visible, not loading, and next page exists
    if (entries[0].isIntersecting && !isLoading && nextPageUrl) {
        console.log("Automatic load triggered by scroll...");
        loadVehicles();
    }
}, { threshold: 0.1 });

document.addEventListener('DOMContentLoaded', () => {
    loadVehicleTypes();
    loadVehicles();
    
    // Start bottom detection
    const sentinel = document.getElementById('scroll-sentinel');
    if (sentinel) observer.observe(sentinel);
});

document.addEventListener('DOMContentLoaded', () => {
    loadVehicleTypes();
    loadVehicles();
});
