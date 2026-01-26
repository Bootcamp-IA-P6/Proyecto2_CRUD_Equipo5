// renting/static/renting/js/layout.js

function toggleSidebar() {
    const sidebar = document.getElementById('main-sidebar');
    sidebar.classList.toggle('active');
}

// renting/static/renting/js/layout.js

async function updateSidebar() {
    const container = document.getElementById('sidebar-auth-content');
    if (!container) return;
    
    if (Auth.isLoggedIn()) {
        // 유저 정보 API 호출 (우리가 만든 /api/users/me/ 사용)
        let userName = "User";
        try {
            const res = await fetchWithAuth('/api/users/me/');
            const data = await res.json();
            userName = data.first_name || "User";
        } catch (e) { console.error("User info error", e); }

        container.innerHTML = `
            <h6 class="text-uppercase text-muted small mb-4 fw-bold">Welcome, ${userName}!</h6>
            <ul class="sidebar-menu">
                <li><a href="/">Explore Vehicles</a></li>
                <li><a href="/reservations/">My Reservations</a></li>
                <li><a href="/reservations/create/">Book a Vehicle</a></li>
                <li><a href="#">My Info</a></li>
                <hr>
                <li><button onclick="logout()" class="text-danger">Logout</button></li>
            </ul>
        `;
    } else {
        container.innerHTML = `
            <h6 class="text-uppercase text-muted small mb-4 fw-bold">Welcome, Guest</h6>
            <p class="small text-muted">Sign in to book your next vehicle.</p>
            <ul class="sidebar-menu">
                <li><a href="/login/">Login</a></li>
                <li><a href="/register/">Sign Up</a></li>
            </ul>
        `;
    }
}

// 클릭 외부 시 사이드바 닫기 (추가하면 좋음)
document.addEventListener('click', (e) => {
    const sidebar = document.getElementById('main-sidebar');
    const toggleBtn = document.querySelector('.nav-toggle-btn');
    if (sidebar.classList.contains('active') && !sidebar.contains(e.target) && e.target !== toggleBtn) {
        sidebar.classList.remove('active');
    }
});

document.addEventListener('DOMContentLoaded', updateSidebar);