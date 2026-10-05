
import pytest

from app import app
from data.inventory import inventory


@pytest.fixture
def client():
    app.config["TESTING"] = True

    with app.test_client() as client:
        yield client


@pytest.fixture
def reset_inventory():
    original_inventory = inventory.copy()
    yield
    inventory.clear()
    inventory.extend(original_inventory)


def test_home(client):
    response = client.get("/")

    assert response.status_code == 200
    assert response.get_json()["message"] == "Inventory Management API"


def test_get_inventory(client):
    response = client.get("/inventory")

    assert response.status_code == 200
    assert isinstance(response.get_json(), list)


def test_get_single_inventory_item(client, reset_inventory):
    response = client.get("/inventory/1")

    assert response.status_code == 200
    assert response.get_json()["id"] == 1


def test_get_missing_inventory_item(client):
    response = client.get("/inventory/99999")

    assert response.status_code == 404
    assert response.get_json()["error"] == "Inventory item not found"


def test_create_inventory_item(client, reset_inventory):
    response = client.post(
        "/inventory",
        json={
            "product_name": "Test Product",
            "brands": "Test Brand",
            "price": 100,
            "stock": 10
        }
    )

    assert response.status_code == 201

    data = response.get_json()

    assert data["product_name"] == "Test Product"
    assert data["price"] == 100
    assert data["stock"] == 10


def test_create_inventory_item_without_name(client):
    response = client.post(
        "/inventory",
        json={
            "price": 100,
            "stock": 10
        }
    )

    assert response.status_code == 400
    assert response.get_json()["error"] == "product_name is required"


def test_create_inventory_item_with_negative_price(client):
    response = client.post(
        "/inventory",
        json={
            "product_name": "Test Product",
            "price": -100,
            "stock": 10
        }
    )

    assert response.status_code == 400
    assert response.get_json()["error"] == "price cannot be negative"


def test_update_inventory_item(client, reset_inventory):
    response = client.patch(
        "/inventory/1",
        json={
            "price": 999,
            "stock": 50
        }
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["price"] == 999
    assert data["stock"] == 50


def test_update_missing_inventory_item(client):
    response = client.patch(
        "/inventory/99999",
        json={
            "price": 500
        }
    )

    assert response.status_code == 404


def test_delete_inventory_item(client, reset_inventory):
    item_id = inventory[0]["id"]

    response = client.delete(
        f"/inventory/{item_id}"
    )

    assert response.status_code == 200
    assert response.get_json()["message"] == "Inventory item deleted successfully"


def test_delete_missing_inventory_item(client):
    response = client.delete("/inventory/99999")

    assert response.status_code == 404

