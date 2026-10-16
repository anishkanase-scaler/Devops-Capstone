import React, { useEffect, useState } from 'react';
import { createRoot } from 'react-dom/client';
import './styles.css';

const API = '/api/products';
const CATEGORIES = ['All', 'Beauty', 'Accessories', 'Home', 'Stationery'];
const EMPTY_FORM = { name: '', emoji: '🎀', category: 'Beauty', price: '', stock: 0 };

// fetch() wrapper: sends JSON, turns FastAPI error responses into readable messages.
async function request(url, options = {}) {
  const res = await fetch(url, { headers: { 'Content-Type': 'application/json' }, ...options });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    const detail = Array.isArray(body.detail) ? body.detail.map((d) => d.msg).join(', ') : body.detail;
    throw new Error(detail || `Request failed (${res.status})`);
  }
  return res.status === 204 ? null : res.json();
}

function App() {
  const [products, setProducts] = useState([]);
  const [category, setCategory] = useState('All');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [editing, setEditing] = useState(null); // null = form closed, {} = new product, {...product} = edit

  // ---------- Read (GET) ----------
  const load = async () => {
    try {
      setError('');
      const url = category === 'All' ? API : `${API}?category=${encodeURIComponent(category)}`;
      setProducts(await request(url));
    } catch {
      setProducts([]);
      setError('Could not reach the backend. Start it on port 8000, then refresh.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, [category]);

  // ---------- Delete (DELETE) ----------
  const remove = async (product) => {
    if (!confirm(`Delete "${product.name}"?`)) return;
    try {
      await request(`${API}/${product.id}`, { method: 'DELETE' });
      load();
    } catch (err) {
      setError(err.message);
    }
  };

  const inStock = products.reduce((sum, p) => sum + p.stock, 0);
  const soldOut = products.filter((p) => p.stock === 0).length;

  return (
    <>
      <header className="header">
        <div className="wrap header-in">
          <div className="logo">🌸 Petal Shop</div>
          <button className="btn" onClick={() => setEditing({})}>+ Add product</button>
        </div>
      </header>

      <main className="wrap">
        {error && <div className="error">{error}</div>}

        <section className="stats">
          <Stat value={products.length} label="Products" />
          <Stat value={inStock} label="Items in stock" />
          <Stat value={soldOut} label="Sold out" />
        </section>

        <div className="chips">
          {CATEGORIES.map((c) => (
            <button key={c} className={`chip ${c === category ? 'on' : ''}`} onClick={() => setCategory(c)}>{c}</button>
          ))}
        </div>

        <div className="grid">
          {loading && <p className="empty">Loading products…</p>}
          {!loading && !products.length && <p className="empty">No products here yet. Add one! 🌸</p>}
          {products.map((p) => (
            <ProductCard key={p.id} product={p} onEdit={() => setEditing(p)} onDelete={() => remove(p)} />
          ))}
        </div>
      </main>

      {editing && (
        <ProductForm product={editing} onClose={() => setEditing(null)} onSaved={() => { setEditing(null); load(); }} />
      )}
    </>
  );
}

function Stat({ value, label }) {
  return <div className="stat"><span>{value}</span>{label}</div>;
}

function ProductCard({ product: p, onEdit, onDelete }) {
  const badge = p.stock === 0 ? <span className="badge out">Sold out</span>
    : p.stock < 5 ? <span className="badge low">Only {p.stock} left</span>
    : <span className="badge">{p.stock} in stock</span>;
  return (
    <article className="card">
      <div className="thumb">{p.emoji}</div>
      <div className="cat">{p.category}</div>
      <div className="name">{p.name}</div>
      <div className="price">₹{p.price}</div>
      {badge}
      <div className="actions">
        <button className="btn small ghost" onClick={onEdit}>Edit</button>
        <button className="btn small danger" onClick={onDelete}>Delete</button>
      </div>
    </article>
  );
}

// ---------- Create (POST) and Update (PUT) ----------
function ProductForm({ product, onClose, onSaved }) {
  const isEdit = Boolean(product.id);
  const [form, setForm] = useState(isEdit ? product : EMPTY_FORM);
  const [error, setError] = useState('');
  const set = (field) => (e) => setForm({ ...form, [field]: e.target.value });

  const save = async (e) => {
    e.preventDefault();
    const body = JSON.stringify({
      name: form.name, emoji: form.emoji, category: form.category,
      price: Number(form.price), stock: Number(form.stock),
    });
    try {
      if (isEdit) await request(`${API}/${product.id}`, { method: 'PUT', body });
      else await request(API, { method: 'POST', body });
      onSaved();
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className="backdrop" onClick={(e) => e.target === e.currentTarget && onClose()}>
      <form className="modal" onSubmit={save}>
        <h2>{isEdit ? 'Edit product' : 'Add product'}</h2>
        <label>Name <input value={form.name} onChange={set('name')} required maxLength={100} placeholder="Cherry Lip Gloss" /></label>
        <div className="two">
          <label>Emoji <input value={form.emoji} onChange={set('emoji')} maxLength={8} /></label>
          <label>Category
            <select value={form.category} onChange={set('category')}>
              {CATEGORIES.slice(1).map((c) => <option key={c}>{c}</option>)}
            </select>
          </label>
        </div>
        <div className="two">
          <label>Price (₹) <input type="number" min="0" value={form.price} onChange={set('price')} required /></label>
          <label>Stock <input type="number" min="0" value={form.stock} onChange={set('stock')} required /></label>
        </div>
        {error && <p className="error">{error}</p>}
        <div className="form-actions">
          <button type="button" className="btn ghost" onClick={onClose}>Cancel</button>
          <button type="submit" className="btn">Save</button>
        </div>
      </form>
    </div>
  );
}

createRoot(document.getElementById('root')).render(<App />);
