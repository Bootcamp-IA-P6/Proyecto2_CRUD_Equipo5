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
 * 모든 API 요청에서 사용할 래퍼 함수 (토큰 자동 주입 + 만료 시 자동 갱신)
 */
async function fetchWithAuth(url, options = {}) {
    let tokens = Auth.getTokens();
    if (!tokens) {
        window.location.href = "/login/?reason=expired";
        return null;
    }

    // 기본 헤더 설정
    if (!options.headers) options.headers = {};
    options.headers['Authorization'] = `Bearer ${tokens.access}`;
    options.headers['Content-Type'] = 'application/json';

    let response = await fetch(url, options);

    // 401 Unauthorized 발생 시 토큰 갱신 시도
    if (response.status === 401) {
        const refreshed = await Auth.refreshAccessToken();
        if (refreshed) {
            // 갱신 성공 시 새 토큰으로 딱 한 번 더 재시도
            tokens = Auth.getTokens();
            options.headers['Authorization'] = `Bearer ${tokens.access}`;
            response = await fetch(url, options);
        } else {
            // 갱신 실패 시 로그아웃
            Auth.clear();
            window.location.href = "/login/?reason=expired";
            return null;
        }
    }
    return response;
}

function logout() {
    Auth.clear();
    window.location.href = "/login/";
}