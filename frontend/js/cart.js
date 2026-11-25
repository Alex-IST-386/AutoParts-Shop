document.addEventListener('DOMContentLoaded', () => { renderCart(); });

function getCart() { return JSON.parse(localStorage.getItem('cart')) || []; }

function renderCart() {
    const cart = getCart();
    const container = document.getElementById('cart-items');
    const totalEl = document.getElementById('total-price');
    if (cart.length === 0) { container.innerHTML = '<p>Корзина пуста.</p>'; totalEl.textContent = '0'; return; }

    container.innerHTML = '';
    let total = 0;
    cart.forEach((item, index) => {
        const itemTotal = item.price * item.quantity;
        total += itemTotal;
        container.innerHTML += `
            <div class="cart-item">
                <div><b>${item.name}</b><br><small>${item.article}</small></div>
                <div>${item.quantity} шт. x ${item.price} = <b>${itemTotal} ₽</b></div>
                <button class="btn-secondary" onclick="removeFromCart(${index})">Удалить</button>
            </div>
        `;
    });
    totalEl.textContent = total;
}

function removeFromCart(index) {
    let cart = getCart();
    cart.splice(index, 1);
    localStorage.setItem('cart', JSON.stringify(cart));
    renderCart();
}

document.getElementById('checkout-btn')?.addEventListener('click', async () => {
    const cart = getCart();
    if (cart.length === 0) { alert('Корзина пуста!'); return; }

    // 1. Создаем чек
    const saleRes = await fetchWithAuth('/sales/', { method: 'POST' });
    if (!saleRes || !saleRes.ok) { alert('Ошибка создания чека'); return; }
    const sale = await saleRes.json();

    // 2. Добавляем позиции в чек
    for (const item of cart) {
        const itemRes = await fetchWithAuth('/sales/items/', {
            method: 'POST',
            body: JSON.stringify({
                quantity: item.quantity,
                price_at_moment: item.price, // Отправляем для схемы, но бэкенд возьмет свою цену
                sale_id: sale.id,
                part_id: item.id
            })
        });
        if (!itemRes.ok) { alert(`Ошибка при добавлении ${item.name}. Возможно, нет на складе.`); return; }
    }

    alert('Чек успешно пробит!');
    localStorage.removeItem('cart');
    window.location.href = 'parts.html';
});