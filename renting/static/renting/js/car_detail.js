// renting/static/renting/js/car_detail.js

/**
 * Helper function to check if image URL exists/loads successfully
 */
function checkImageExists(url) {
    return new Promise((resolve) => {
        const img = new Image();
        img.onload = () => resolve(true);  // Load successful
        img.onerror = () => resolve(false); // Load failed (file missing)
        img.src = url;
    });
}

/**
 * Load car details from API and populate page
 */
async function loadCarDetail() {
    const pathParts = window.location.pathname.split('/');
    const carId = pathParts[pathParts.length - 2];

    const response = await fetchWithAuth(`/api/cars/${carId}/`);
    if (!response || !response.ok) return;

    const c = await response.json();

    // Populate car detail fields from API response
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

    // --- Image carousel logic (core functionality) ---
    const carouselInner = document.getElementById('carousel-images');
    carouselInner.innerHTML = ''; // Remove spinner

    const brandLow = c.brand_name.toLowerCase().replace(/\s/g, '_');
    const modelLow = c.car_model_name.toLowerCase().replace(/\s/g, '_');
    
    const potentialImages = [];
    
    // 1. Use DB image if available (first priority)
    if (c.car_model_image) potentialImages.push(c.car_model_image);

    // 2. Add static fallback paths (check images 1-3)
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

    // 3. Show placeholder if no images loaded
    if (!loadedAny) {
        carouselInner.innerHTML = `
            <div class="carousel-item active">
                <img src="/static/renting/images/cars/placeholder.png" class="d-block w-100 rounded" alt="No image available">
            </div>
        `;
    }

    // Initialize Bootstrap carousel after images loaded
    const carCarouselEl = document.querySelector('#carCarousel');
    
    // Auto-rotate only if 2+ images
    if (loadedAny && carouselInner.children.length > 1) {
        new bootstrap.Carousel(carCarouselEl, {
            interval: 3000, // Switch every 3 seconds
            ride: 'carousel'
        });
    } else {
        // Hide controls if single image (optional)
        const controls = carCarouselEl.querySelectorAll('.carousel-control-prev, .carousel-control-next');
        controls.forEach(c => c.style.display = 'none');
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', loadCarDetail);
