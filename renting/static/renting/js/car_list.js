// renting/static/renting/js/car_list.js

async function loadCars() {
    const response = await fetchWithAuth('/api/cars/'); 
    if (!response) return;

    const data = await response.json();
    const items = Array.isArray(data) ? data : (data.results || []);
    
    const tbody = document.getElementById('car-list-body');
    
    if (items.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" class="text-center">No vehicles found.</td></tr>';
        return;
    }

    tbody.innerHTML = items.map(c => {
        // Use the API image or the static placeholder
        const imageUrl = c.car_model_image || '/static/renting/images/cars/car_basic.jpg';
        
        return `
            <tr>
                <td class="text-center">
                    <img src="${imageUrl}" 
                         alt="${c.car_model_name}" 
                         class="img-thumbnail"
                         style="width: 100px; height: 60px; object-fit: cover;">
                </td>
                <td><strong>${c.brand_name || '-'}</strong></td>
                <td>${c.car_model_name}</td>
                <td><span class="badge bg-secondary text-uppercase">${c.license_plate}</span></td>
                <td>${c.mileage ? c.mileage.toLocaleString() + ' km' : '-'}</td>
            </tr>
        `;
    }).join('');
}

// Initialize when the DOM is ready
document.addEventListener('DOMContentLoaded', loadCars);