const API_URL = "http://127.0.0.1:8000";

function getToken() { return localStorage.getItem('access_token'); }

async function fetchWithAuth(endpoint, options = {}) {
    const token = getToken();
    if (!token) { window.location.href = 'login.html'; return; }
    const headers = { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json', ...options.headers };
    try {
        const response = await fetch(`${API_URL}${endpoint}`, { ...options, headers });
        if (response.status === 401) { localStorage.removeItem('access_token'); window.location.href = 'login.html'; return; }
        return response;
    } catch (e) { console.error(e); }
}

// Добавь в конец файла api.js
function logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('cart'); // Заодно чистим корзину
    window.location.href = 'login.html';
}