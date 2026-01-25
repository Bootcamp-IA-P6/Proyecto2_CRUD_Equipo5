// renting/static/renting/js/car_detail.js

/**
 * 이미지 URL이 유효한지(존재하는지) 확인하는 헬퍼 함수
 */
function checkImageExists(url) {
    return new Promise((resolve) => {
        const img = new Image();
        img.onload = () => resolve(true);  // 로드 성공
        img.onerror = () => resolve(false); // 로드 실패 (파일 없음)
        img.src = url;
    });
}

async function loadCarDetail() {
    const pathParts = window.location.pathname.split('/');
    const carId = pathParts[pathParts.length - 2];

    const response = await fetchWithAuth(`/api/cars/${carId}/`);
    if (!response || !response.ok) return;

    const c = await response.json();

    // [기존 데이터 매핑 로직은 동일하게 유지]
    document.getElementById('car-brand').innerText = c.brand_name;
    document.getElementById('car-name').innerText = c.car_model_name.replace('_', ' ');
    document.getElementById('breadcrumb-model').innerText = c.car_model_name;
    document.getElementById('car-price').innerText = `${c.daily_price}€`;
    document.getElementById('car-seats').innerText = c.seats || '-';
    document.getElementById('car-vtype').innerText = c.vehicle_type_name || '-';
    document.getElementById('car-trans').innerText = c.transmission_name || '-';
    document.getElementById('car-fuel').innerText = c.fuel_type_name || '-';
    document.getElementById('car-plate').innerText = c.license_plate;
    document.getElementById('reserve-link').href = `/reservations/create/?car=${c.id}`;

    // --- 🖼 캐러셀 이미지 로직 (핵심) ---
    const carouselInner = document.getElementById('carousel-images');
    carouselInner.innerHTML = ''; // 스피너 제거

    const brandLow = c.brand_name.toLowerCase().replace(/\s/g, '_');
    const modelLow = c.car_model_name.toLowerCase().replace(/\s/g, '_');
    
    const potentialImages = [];
    
    // 1. DB에 등록된 이미지가 있다면 첫 번째 후보로 등록
    if (c.car_model_image) potentialImages.push(c.car_model_image);

    // 2. 야매(Static) 경로 후보들 등록 (1번부터 3번까지 체크)
    for (let i = 1; i <= 3; i++) {
        potentialImages.push(`/static/renting/images/cars/${brandLow}_${modelLow}_${i}.jpg`);
    }

    let loadedAny = false;

    for (const url of potentialImages) {
        const exists = await checkImageExists(url);
        if (exists) {
            const item = document.createElement('div');
            item.className = `carousel-item ${!loadedAny ? 'active' : ''}`;
            item.innerHTML = `<img src="${url}" class="d-block w-100 rounded" style="height: 400px; object-fit: cover;" alt="Vehicle">`;
            carouselInner.appendChild(item);
            loadedAny = true;
        }
    }

    // 3. 만약 단 하나의 이미지도 로드되지 않았다면 placeholder 표시
    if (!loadedAny) {
        carouselInner.innerHTML = `
            <div class="carousel-item active">
                <img src="/static/renting/images/cars/placeholder.png" class="d-block w-100 rounded" alt="No image available">
            </div>
        `;
    }

    // 🔥 [핵심 추가] 이미지가 다 들어간 후 부트스트랩 캐러셀 수동 초기화
    const carCarouselEl = document.querySelector('#carCarousel');
    
    // 만약 이미지가 2개 이상일 때만 자동으로 돌아가게 설정
    if (loadedAny && carouselInner.children.length > 1) {
        new bootstrap.Carousel(carCarouselEl, {
            interval: 3000, // 3초마다 전환
            ride: 'carousel'
        });
    } else {
        // 이미지가 하나뿐이면 컨트롤 버튼(화살표) 숨기기 (선택 사항)
        const controls = carCarouselEl.querySelectorAll('.carousel-control-prev, .carousel-control-next');
        controls.forEach(c => c.style.display = 'none');
    }
}

document.addEventListener('DOMContentLoaded', loadCarDetail);