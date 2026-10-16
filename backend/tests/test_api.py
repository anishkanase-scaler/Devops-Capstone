import pytest


# ---------- Service endpoints ----------

def test_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"service": "Petal Shop API", "version": "1.0.0", "docs": "/docs"}


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "UP"}


def test_ready_checks_database(client):
    response = client.get("/ready")
    assert response.status_code == 200
    assert response.json() == {"status": "READY"}


def test_metrics_exposed(client):
    client.get("/health")
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "http_requests_total" in response.text


# ---------- GET ----------

def test_list_returns_seeded_products(client):
    response = client.get("/api/products")
    assert response.status_code == 200
    names = [p["name"] for p in response.json()]
    assert len(names) == 6  # seeded by migration 0002
    assert "Rose Quartz Roller" in names


def test_get_product(client, product):
    response = client.get(f"/api/products/{product['id']}")
    assert response.status_code == 200
    assert response.json()["name"] == "Cherry Lip Gloss"


def test_get_missing_product_returns_404(client):
    response = client.get("/api/products/999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Product not found"}


def test_list_filters_by_category(client, product):
    beauty = client.get("/api/products", params={"category": "Beauty"}).json()
    assert {p["category"] for p in beauty} == {"Beauty"}
    assert [p["name"] for p in beauty] == ["Rose Quartz Roller", "Strawberry Lip Balm", "Cherry Lip Gloss"]

    stationery = client.get("/api/products", params={"category": "Stationery"}).json()
    assert [p["name"] for p in stationery] == ["Pastel Notebook"]


# ---------- POST ----------

def test_create_product(client):
    response = client.post(
        "/api/products",
        json={"name": "Peony Hair Clip", "emoji": "🌸", "category": "Accessories", "price": 129, "stock": 30},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["id"] > 0
    assert body["name"] == "Peony Hair Clip"
    assert body["price"] == 129
    assert "created_at" in body
    assert len(client.get("/api/products").json()) == 7  # 6 seeded + 1 new


def test_create_product_uses_defaults(client):
    body = client.post("/api/products", json={"name": "Gel Pen Set", "category": "Stationery", "price": 149}).json()
    assert body["emoji"] == "🎀"
    assert body["stock"] == 0


@pytest.mark.parametrize(
    "payload",
    [
        {"name": "", "category": "Beauty", "price": 100},              # empty name
        {"name": "Toy Car", "category": "Toys", "price": 100},         # unknown category
        {"name": "Mug", "category": "Home", "price": -1},              # negative price
        {"name": "Mug", "category": "Home", "price": 100, "stock": -5},  # negative stock
        {"category": "Home", "price": 100},                            # missing name
    ],
    ids=["empty-name", "unknown-category", "negative-price", "negative-stock", "missing-name"],
)
def test_create_product_rejects_invalid_input(client, payload):
    response = client.post("/api/products", json=payload)
    assert response.status_code == 422


# ---------- PUT ----------

def test_update_product_changes_only_sent_fields(client, product):
    response = client.put(f"/api/products/{product['id']}", json={"price": 699})
    assert response.status_code == 200
    body = response.json()
    assert body["price"] == 699
    assert body["name"] == product["name"]
    assert body["stock"] == product["stock"]


def test_update_is_saved(client, product):
    client.put(f"/api/products/{product['id']}", json={"stock": 0})
    assert client.get(f"/api/products/{product['id']}").json()["stock"] == 0


def test_update_missing_product_returns_404(client):
    response = client.put("/api/products/999", json={"price": 10})
    assert response.status_code == 404


def test_update_rejects_invalid_input(client, product):
    response = client.put(f"/api/products/{product['id']}", json={"price": -10})
    assert response.status_code == 422


# ---------- DELETE ----------

def test_delete_product(client, product):
    response = client.delete(f"/api/products/{product['id']}")
    assert response.status_code == 204
    assert client.get(f"/api/products/{product['id']}").status_code == 404
    assert len(client.get("/api/products").json()) == 6  # back to just the seeded products


def test_delete_missing_product_returns_404(client):
    response = client.delete("/api/products/999")
    assert response.status_code == 404
