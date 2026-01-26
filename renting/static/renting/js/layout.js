// renting/static/renting/js/layout.js

/**
 * Toggle main sidebar visibility
 */
function toggleSidebar() {
    const sidebar = document.getElementById('main-sidebar');
    sidebar.classList.toggle('active');
}

/**
 * Update sidebar content based on authentication status
 */
async function updateSidebar() {
    const container = document.getElementById('sidebar-auth-content');
    if (!container) return;
    
    if (Auth.isLoggedIn()) {
        let userName = "User";
        try {
            // Updated: Use latest backend API endpoint
            const res = await fetchWithAuth('/api/profile/me/');
            if (res && res.ok) {
                const data = await res.json();
                userName = data.first_name || "User";
            }
        } catch (e) { 
            console.error("User info error", e); 
        }
        
        container.innerHTML = `
            <h6 class="text-uppercase text-muted small mb-4 fw-bold">Welcome, ${userName}!</h6>
            <ul class="sidebar-menu">
                <li><a href="/">Explore Vehicles</a></li>
                <li><a href="/reservations/">My Reservations</a></li>
                <li><a href="/reservations/create/">Book a Vehicle</a></li>
                <li><a href="/profile/">My Info</a></li>
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

// Close sidebar when clicking outside (recommended addition)
document.addEventListener('click', (e) => {
    const sidebar = document.getElementById('main-sidebar');
    const toggleBtn = document.querySelector('.nav-toggle-btn');
    if (sidebar.classList.contains('active') && !sidebar.contains(e.target) && e.target !== toggleBtn) {
        sidebar.classList.remove('active');
    }
});

// Initialize sidebar on DOM load
document.addEventListener('DOMContentLoaded', updateSidebar);
