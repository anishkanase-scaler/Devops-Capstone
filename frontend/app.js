// Every number and card on the page comes from the backend API.
const BACKEND_URL = 'http://localhost:8000';
const API = `${BACKEND_URL}/api/products`;
const CATEGORIES = ['All', 'Beauty', 'Accessories', 'Home', 'Stationery'];

const $ = (id) => document.getElementById(id);
const dialog = $('dialog');
const form = $('form');

let products = [];
let category = 'All';
let editingId = null; // null = adding a new product

const escapeHtml = (s) => String(s).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

async function request(url, options = {}) {
  const res = await fetch(url, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    const detail = Array.isArray(body.detail) ? body.detail.map((d) => d.msg).join(', ') : body.detail;
    throw new Error(detail || `Request failed (${res.status})`);
  }
  return res.status === 204 ? null : res.json();
}

function showError(message) {
  $('error').textContent = message;
  $('error').hidden = !message;
}

// ---------- Read (GET) ----------
async function loadProducts() {
  try {
    const url = category === 'All' ? API : `${API}?category=${encodeURIComponent(category)}`;
    products = await request(url);
    showError('');
  } catch {
    products = [];
    showError('Could not reach the backend. Is it running?');
  }
  render();
}

function render() {
  $('stat-total').textContent = products.length;
  $('stat-stock').textContent = products.reduce((sum, p) => sum + p.stock, 0);
  $('stat-out').textContent = products.filter((p) => p.stock === 0).length;

  $('chips').innerHTML = CATEGORIES.map(
    (c) => `<button class="chip ${c === category ? 'on' : ''}" data-category="${c}">${c}</button>`
  ).join('');

  if (!products.length) {
    $('grid').innerHTML = '<p class="empty">No products here yet. Add one! 🌸</p>';
    return;
  }

  $('grid').innerHTML = products.map((p) => {
    const badge = p.stock === 0 ? '<span class="badge out">Sold out</span>'
      : p.stock < 5 ? `<span class="badge low">Only ${p.stock} left</span>`
      : `<span class="badge">${p.stock} in stock</span>`;
    return `
      <article class="card">
        <div class="thumb">${escapeHtml(p.emoji)}</div>
        <div class="cat">${escapeHtml(p.category)}</div>
        <div class="name">${escapeHtml(p.name)}</div>
        <div class="price">₹${p.price}</div>
        ${badge}
        <div class="actions">
          <button class="btn small ghost" data-edit="${p.id}">Edit</button>
          <button class="btn small danger" data-delete="${p.id}">Delete</button>
        </div>
      </article>`;
  }).join('');
}

// ---------- Create (POST) and Update (PUT) ----------
function openForm(product) {
  editingId = product ? product.id : null;
  $('form-title').textContent = product ? 'Edit product' : 'Add product';
  $('form-error').hidden = true;
  form.reset();
  if (product) {
    for (const field of ['name', 'emoji', 'category', 'price', 'stock']) form.elements[field].value = product[field];
  }
  dialog.showModal();
}

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  const data = Object.fromEntries(new FormData(form));
  data.price = Number(data.price);
  data.stock = Number(data.stock);
  try {
    if (editingId) {
      await request(`${API}/${editingId}`, { method: 'PUT', body: JSON.stringify(data) });
    } else {
      await request(API, { method: 'POST', body: JSON.stringify(data) });
    }
    dialog.close();
    loadProducts();
  } catch (err) {
    $('form-error').textContent = err.message;
    $('form-error').hidden = false;
  }
});

// ---------- Delete (DELETE) ----------
async function deleteProduct(id) {
  const product = products.find((p) => p.id === id);
  if (!confirm(`Delete "${product.name}"?`)) return;
  try {
    await request(`${API}/${id}`, { method: 'DELETE' });
    loadProducts();
  } catch (err) {
    showError(err.message);
  }
}

// ---------- Buttons ----------
document.addEventListener('click', (event) => {
  const t = event.target;
  if (t.dataset.category) { category = t.dataset.category; loadProducts(); }
  if (t.dataset.edit) openForm(products.find((p) => p.id === Number(t.dataset.edit)));
  if (t.dataset.delete) deleteProduct(Number(t.dataset.delete));
});
$('add-btn').addEventListener('click', () => openForm(null));
$('cancel').addEventListener('click', () => dialog.close());

loadProducts();
