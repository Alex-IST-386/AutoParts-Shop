document.addEventListener('DOMContentLoaded', async () => {
    if (!document.getElementById('parts-grid')) return;

    const res = await fetchWithAuth('/parts/');
    if (!res || !res.ok) return;

    const parts = await res.json();
    const grid = document.getElementById('parts-grid');
    grid.innerHTML = '';

    parts.forEach(part => {
        const lowStock = part.stock_quantity < 5 ? `<div class="badge-low-stock">⚠ Мало на складе</div>` : '';
        const card = document.createElement('div');
        card.className = 'part-card';
        card.innerHTML = `
            <div class="part-article">Артикул: ${part.article}</div>
            <div class="part-name">${part.name}</div>
            <div class="part-price">${part.price} ₽</div>
            ${lowStock}
            <div class="part-stock">На складе: ${part.stock_quantity} шт.</div>
            <div class="card-actions">
                <button class="btn-secondary" onclick="showAnalogs(${part.id}, this)">Аналоги</button>
                <button class="btn-primary" onclick="addToCart(${part.id}, '${part.name}', ${part.price}, '${part.article}')">В корзину</button>
            </div>
            <div class="analogs-container" id="analogs-${part.id}"></div>
        `;
        grid.appendChild(card);
    });
});

// Показываем аналоги (BFS)
async function showAnalogs(id, btn) {
    const container = document.getElementById(`analogs-${id}`);
    if (container.style.display === 'block') { container.style.display = 'none'; btn.textContent = 'Аналоги'; return; }

    container.style.display = 'block';
    btn.textContent = 'Скрыть';
    container.innerHTML = 'Поиск...';

    // ТУТ МЫ ДЕЛАЕМ ЗАПРОС К BFS АЛГОРИТМУ НА БЭКЕНДЕ
    const res = await fetchWithAuth(`/parts/${id}/analogs`);
    if (res && res.ok) {
        const analogs = await res.json();
        if (analogs.length === 0) { container.innerHTML = '<div style="font-size:12px">Аналоги не найдены</div>'; return; }
        let html = '';
        analogs.forEach(a => { html += `<div class="analog-item">${a.article} (${a.name}) — ${a.price} ₽</div>`; });
        container.innerHTML = html;
    }
}

function addToCart(id, name, price, article) {
    let cart = JSON.parse(localStorage.getItem('cart')) || [];
    const existing = cart.find(i => i.id === id);
    if (existing) { existing.quantity += 1; }
    else { cart.push({ id, name, price, article, quantity: 1 }); }
    localStorage.setItem('cart', JSON.stringify(cart));
    alert(`Товар "${name}" добавлен в корзину!`);
}