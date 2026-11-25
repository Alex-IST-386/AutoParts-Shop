function togglePassword(id, btn) {
    const input = document.getElementById(id);
    if (input.type === 'password') { input.type = 'text'; btn.textContent = 'Скрыть'; }
    else { input.type = 'password'; btn.textContent = 'Посмотреть'; }
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
                window.location.href = 'parts.html';
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
                    role: 'seller',
                    email: document.getElementById('email-register').value || null
                })
            });
            if (res.ok) { alert('Успешно! Войдите.'); window.location.href = 'login.html'; }
            else { const err = await res.json(); alert(`Ошибка: ${err.detail}`); }
        } catch (e) { alert('Сервер не отвечает'); }
    });
}