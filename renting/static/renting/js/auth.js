// renting/static/renting/js/auth.js

const Auth = {
    getTokens: () => JSON.parse(localStorage.getItem('tokens')),
    saveTokens: (tokens) => localStorage.setItem('tokens', JSON.stringify(tokens)),
    clear: () => localStorage.removeItem('tokens'),
    isLoggedIn: () => !!localStorage.getItem('tokens')
};

/**
 * Global fetch wrapper with automatic JWT attachment and 401 handling
 */
async function fetchWithAuth(url, options = {}) {
    const tokens = Auth.getTokens();
    if (!tokens) {
        window.location.href = "/login/?reason=expired";
        return null;
    }

    options.headers = {
        ...options.headers,
        'Authorization': `Bearer ${tokens.access}`,
        'Content-Type': 'application/json'
    };

    try {
        const response = await fetch(url, options);

        if (response.status === 401) {
            Auth.clear();
            window.location.href = "/login/?reason=expired";
            return null;
        }
        return response;
    } catch (error) {
        console.error("Auth Fetch Error:", error);
        return null;
    }
}

function logout() {
    Auth.clear();
    window.location.href = "/login/";
}