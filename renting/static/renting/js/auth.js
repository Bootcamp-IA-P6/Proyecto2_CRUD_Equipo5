// renting/static/renting/js/auth.js

const Auth = {
    getTokens: () => JSON.parse(localStorage.getItem('tokens')),
    
    saveTokens: (tokens) => {
        const current = Auth.getTokens() || {};
        localStorage.setItem('tokens', JSON.stringify({ ...current, ...tokens }));
    },
    
    clear: () => localStorage.removeItem('tokens'),
    
    isLoggedIn: () => !!localStorage.getItem('tokens'),

    /**
     * 중앙 집중식 에러 파서: 서버 응답에서 에러 메시지를 추출합니다.
     */
    parseError: async (response) => {
        try {
            const data = await response.json();
            // 커스텀 예외 핸들러의 'details' 키 또는 기본 'detail' 키 확인
            return data.details || data;
        } catch (e) {
            return { detail: "A server error occurred. Please try again later." };
        }
    },

    /**
     * Access 토큰 만료 시 Refresh 토큰으로 갱신 요청
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
 * [UPGRADED] Guest-aware fetch wrapper
 */
async function fetchWithAuth(url, options = {}) {
    const tokens = Auth.getTokens();
    
    if (!options.headers) options.headers = {};
    options.headers['Content-Type'] = 'application/json';

    // ⚠️ 수정: 토큰이 있을 때만 헤더에 추가 (없어도 리다이렉트 안 함)
    if (tokens && tokens.access) {
        options.headers['Authorization'] = `Bearer ${tokens.access}`;
    }

    let response = await fetch(url, options);

    // 401(만료) 발생 시에만 리프레시 시도
    if (response.status === 401 && tokens && tokens.refresh) {
        const refreshed = await Auth.refreshAccessToken();
        if (refreshed) {
            const newTokens = Auth.getTokens();
            options.headers['Authorization'] = `Bearer ${newTokens.access}`;
            response = await fetch(url, options);
        } else {
            // 진짜 만료된 경우만 로그인으로
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