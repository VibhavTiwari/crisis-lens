const API_URL = "http://localhost:8000/api";

async function fetchItems() {
    try {
        const response = await fetch(`${API_URL}/items`);
        const items = await response.json();
        renderList(items);
    } catch (e) {
        console.error(e);
        document.getElementById('item-list').innerHTML = '<p class="error">Failed to load items.</p>';
    }
}

function renderList(items) {
    const list = document.getElementById('item-list');
    list.innerHTML = '';

    items.forEach(item => {
        const el = document.createElement('div');
        el.className = 'item-card';
        el.innerHTML = `
            <div class="item-title">${item.title}</div>
            <div class="item-meta">
                <span>Risk: <span class="${item.risk_score > 0.5 ? 'risk-high' : 'risk-low'}">${item.risk_score}</span></span>
                <span>${item.status}</span>
            </div>
        `;
        el.onclick = () => selectItem(item, el);
        list.appendChild(el);
    });
}

function selectItem(item, el) {
    // Highlight active
    document.querySelectorAll('.item-card').forEach(c => c.classList.remove('active'));
    el.classList.add('active');

    renderDetails(item);
}

function renderDetails(item) {
    const details = document.getElementById('details-panel');
    details.innerHTML = `
        <div class="detail-view">
            <h2>${item.title}</h2>
            <p>${item.text}</p>
            
            <h3>Claims</h3>
            ${item.claims.map(c => `
                <div class="claim-card">
                    <p><strong>Claim:</strong> ${c.text}</p>
                    <p>Veracity: ${c.veracity} | Risk: ${c.risk}</p>
                </div>
            `).join('')}
            
            <div class="actions">
                <button class="btn-verify" onclick="verifyItem('${item.id}', 'verified_true')">Verify as True</button>
                <button class="btn-debunk" onclick="verifyItem('${item.id}', 'verified_false')">Mark as False</button>
            </div>
        </div>
    `;
}

async function verifyItem(id, status) {
    try {
        await fetch(`${API_URL}/items/${id}/verify?status=${status}`, { method: 'POST' });
        alert(`Item marked as ${status}`);
        fetchItems(); // Refresh
        document.getElementById('details-panel').innerHTML = '<div class="empty-state">Select an item to review</div>';
    } catch (e) {
        alert('Error updating status');
    }
}

// Init
// Note: 'def' was a typo in JS, fixing to 'function' or arrow func.
// I used 'async def' above by mistake (python habit). Fixing it now.
fetchItems();
