function togglePassword(id, btn) {
    const input = document.getElementById(id);
    if (input.type === 'password') { input.type = 'text'; btn.textContent = 'Скрыть'; }
    else { input.type = 'password'; btn.textContent = 'Посмотреть'; }
}

// Определяем роль и выбираем страницу
async function redirectByRole(token) {
    try {
        const meRes = await fetch('http://127.0.0.1:8000/users/me', {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (meRes.ok) {
            const me = await meRes.json();
            const routes = {
                admin: 'admin.html',
                supplier: 'suppliers.html',
                user: 'parts.html',
                seller: 'parts.html'
            };
            window.location.href = routes[me.role] || 'parts.html';
            return;
        }
    } catch (e) { console.error(e); }
    // если /users/me недоступен — идём в каталог по умолчанию
    window.location.href = 'parts.html';
}

const loginForm = document.getElementById('login');
if (loginForm) {
    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const formData = new URLSearchParams();
        formData.append('username', document.getElementById('username').value);
        formData.append('password', document.getElementById('password').value);

        try {
            const res = await fetch('http://127.0.0.1:8000/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: formData
            });
            if (res.ok) {
                const data = await res.json();
                localStorage.setItem('access_token', data.access_token);
                await redirectByRole(data.access_token);
            } else { alert('Неверный логин или пароль'); }
        } catch (e) { alert('Сервер не отвечает'); }
    });
}

const registerForm = document.getElementById('register');
if (registerForm) {
    registerForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const pass = document.getElementById('password-register').value;
        if (pass !== document.getElementById('password-repeat').value) {
            alert('Пароли не совпадают!'); return;
        }
        try {
            const res = await fetch('http://127.0.0.1:8000/register', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    username: document.getElementById('username-register').value,
                    password: pass,
                    email: document.getElementById('email-register').value || null
                })
            });
            if (res.ok) {
                // Регистрация токен не возвращает — после неё идём на вход
                alert('Регистрация успешна! Теперь войдите.');
                window.location.href = 'login.html';
            } else {
                const err = await res.json();
                alert(`Ошибка: ${typeof err.detail === 'string' ? err.detail : JSON.stringify(err.detail)}`);
            }
        } catch (e) { alert('Сервер не отвечает'); }
    });
}
