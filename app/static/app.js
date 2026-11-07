// Two tiny fetch() calls so the UI depends on the API: perfect for network mocking practice.
async function loadHealth() {
  const el = document.querySelector('[data-testid="health-badge"]');
  try {
    const res = await fetch('/api/health');
    const data = await res.json();
    el.textContent = 'API: ' + data.status;
    el.dataset.state = data.status;
  } catch (err) {
    el.textContent = 'API: down';
    el.dataset.state = 'down';
  }
}

async function loadStats() {
  const el = document.querySelector('[data-testid="stats"]');
  if (!el) return;
  try {
    const res = await fetch('/api/stats');
    if (!res.ok) throw new Error('HTTP ' + res.status);
    const data = await res.json();
    el.querySelector('[data-testid="stats-total"]').textContent = data.total_books;
    el.querySelector('[data-testid="stats-stock"]').textContent = data.total_stock;
    el.dataset.state = 'ready';
  } catch (err) {
    el.textContent = 'Stats unavailable';
    el.dataset.state = 'error';
  }
}

loadHealth();
loadStats();
