"""Smoke tests for tenant registration, catalog and ledger-backed inventory."""
def auth(client):
    response = client.post("/api/v1/auth/register", json={"organization_name":"Demo Co",
        "full_name":"Demo Owner", "email":"owner@example.com", "password":"StrongPass123!"})
    assert response.status_code == 201, response.text
    return {"Authorization": f"Bearer {response.json()['access_token']}"}

def test_registration_and_health(client):
    assert client.get("/health").json()["status"] == "ok"
    headers = auth(client)
    assert client.get("/api/v1/auth/me", headers=headers).status_code == 200

def test_product_warehouse_and_inventory_ledger(client):
    headers = auth(client)
    product = client.post("/api/v1/products", headers=headers, json={"sku":"SKU-1","name":"Steel Sheet",
        "purchase_price":"100.00","selling_price":"150.00","reorder_level":5}).json()
    warehouse = client.post("/api/v1/warehouses", headers=headers,
        json={"code":"WH-1","name":"Main Warehouse"}).json()
    adjustment = client.post("/api/v1/inventory/adjustments", headers=headers, json={
        "warehouse_id":warehouse["id"],"product_id":product["id"],"quantity":12,
        "direction":"IN","reason":"Opening count verified","idempotency_key":"opening-stock-001"})
    assert adjustment.status_code == 201, adjustment.text
    assert adjustment.json()["after_on_hand"] == 12
    balances = client.get("/api/v1/inventory/balances", headers=headers).json()
    assert balances[0]["available"] == 12
    # Replaying the same idempotency key must not create a second stock movement.
    replay = client.post("/api/v1/inventory/adjustments", headers=headers, json={
        "warehouse_id":warehouse["id"],"product_id":product["id"],"quantity":12,
        "direction":"IN","reason":"Opening count verified","idempotency_key":"opening-stock-001"})
    assert replay.status_code == 201
    assert len(client.get("/api/v1/inventory/movements", headers=headers).json()) == 1

def test_tenant_scoping_hides_other_tenant_products(client):
    owner_a = auth(client)
    client.post("/api/v1/products", headers=owner_a, json={"sku":"A-1","name":"Tenant A item"})
    owner_b = client.post("/api/v1/auth/register", json={"organization_name":"Tenant B",
        "full_name":"Owner B", "email":"b@example.com", "password":"StrongPass123!"}).json()
    headers_b = {"Authorization": f"Bearer {owner_b['access_token']}"}
    assert client.get("/api/v1/products", headers=headers_b).json() == []
