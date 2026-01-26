// renting/static/renting/js/auth.js

/**
 * Global alert function definition (prevents ReferenceError)
 */
window.showGlobalAlert = function(message, type = 'danger') {
    const container = document.getElementById('global-alert-container');
    if (!container) {
        console.error("Alert container not found!");
        alert(message); // Fallback to native alert if container missing
        return;
    }
    container.innerHTML = `
        <div class="alert alert-${type} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>
    `;
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        const alert = container.querySelector('.alert');
        if (alert) {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }
    }, 5000);
};

const Auth = {
    getTokens: () => JSON.parse(localStorage.getItem('tokens')),
    
    saveTokens: (tokens) => {
        const current = Auth.getTokens() || {};
        localStorage.setItem('tokens', JSON.stringify({ ...current, ...tokens }));
    },
    
    clear: () => localStorage.removeItem('tokens'),
    
    isLoggedIn: () => !!localStorage.getItem('tokens'),

    /**
     * Centralized error parser: extracts error messages from server responses
     */
    parseError: async (response) => {
        try {
            const data = await response.json();
            // Check custom handler 'details' key or default 'detail' key
            return data.details || data;
        } catch (e) {
            return { detail: "A server error occurred. Please try again later." };
        }
    },

    /**
     * Refresh access token using refresh token when expired
     */
    refreshAccessToken: async () => {
        const tokens = Auth.getTokens();
        if (!tokens || !tokens.refresh) return false;

        try {
            const response = await fetch('/api/token/refresh/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ refresh: tokens.refresh })
            });

            if (response.ok) {
                const data = await response.json();
                Auth.saveTokens({ access: data.access });
                return true;
            }
        } catch (err) {
            console.error("Token refresh failed:", err);
        }
        return false;
    }
};

/**
 * Guest-aware fetch wrapper with automatic token refresh
 */
async function fetchWithAuth(url, options = {}) {
    const tokens = Auth.getTokens();
    
    if (!options.headers) options.headers = {};
    options.headers['Content-Type'] = 'application/json';

    // Add token header only if tokens exist (no redirect for guests)
    if (tokens && tokens.access) {
        options.headers['Authorization'] = `Bearer ${tokens.access}`;
    }

    let response = await fetch(url, options);

    // Try refresh only on 401 (expired token)
    if (response.status === 401 && tokens && tokens.refresh) {
        const refreshed = await Auth.refreshAccessToken();
        if (refreshed) {
            const newTokens = Auth.getTokens();
            options.headers['Authorization'] = `Bearer ${newTokens.access}`;
            response = await fetch(url, options);
        } else {
            // Real expiration - clear tokens and redirect
            Auth.clear();
            if (window.location.pathname !== '/') {
                window.location.href = "/login/?reason=expired";
            }
        }
    }
    return response;
}

function logout() {
    Auth.clear();
    window.location.href = "/login/";
}
