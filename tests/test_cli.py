
from unittest.mock import Mock, patch

import cli


def test_list_inventory(capsys):
    mock_response = Mock()

    mock_response.status_code = 200

    mock_response.json.return_value = [
        {
            "id": 1,
            "product_name": "Test Product",
            "brands": "Test Brand",
            "price": 100,
            "stock": 10
        }
    ]

    with patch(
        "cli.requests.get",
        return_value=mock_response
    ):

        cli.list_inventory()

    output = capsys.readouterr().out

    assert "Test Product" in output
    assert "Test Brand" in output


def test_get_product(capsys):
    mock_response = Mock()

    mock_response.status_code = 200

    mock_response.json.return_value = {
        "id": 1,
        "product_name": "Test Product",
        "brands": "Test Brand",
        "barcode": "123456",
        "price": 100,
        "stock": 10,
        "ingredients_text": "Sugar",
        "categories": "Snacks"
    }

    with patch(
        "cli.requests.get",
        return_value=mock_response
    ):

        cli.get_product(1)

    output = capsys.readouterr().out

    assert "Test Product" in output
    assert "Test Brand" in output


def test_get_missing_product(capsys):
    mock_response = Mock()

    mock_response.status_code = 404

    with patch(
        "cli.requests.get",
        return_value=mock_response
    ):

        cli.get_product(999)

    output = capsys.readouterr().out

    assert "Product not found" in output


def test_add_product(capsys):
    mock_response = Mock()

    mock_response.status_code = 201

    mock_response.json.return_value = {
        "id": 4,
        "product_name": "Test Product",
        "brands": "Test Brand",
        "price": 100,
        "stock": 10
    }

    args = Mock()

    args.name = "Test Product"
    args.brand = "Test Brand"
    args.price = 100
    args.stock = 10
    args.barcode = "123456"

    with patch(
        "cli.requests.post",
        return_value=mock_response
    ):

        cli.add_product(args)

    output = capsys.readouterr().out

    assert "Product added successfully" in output


def test_update_product(capsys):
    mock_response = Mock()

    mock_response.status_code = 200

    mock_response.json.return_value = {
        "id": 1,
        "product_name": "Test Product",
        "price": 500,
        "stock": 20
    }

    args = Mock()

    args.id = 1
    args.name = None
    args.price = 500
    args.stock = 20

    with patch(
        "cli.requests.patch",
        return_value=mock_response
    ):

        cli.update_product(args)

    output = capsys.readouterr().out

    assert "Product updated successfully" in output


def test_delete_product(capsys):
    mock_response = Mock()

    mock_response.status_code = 200

    mock_response.json.return_value = {
        "message": "Inventory item deleted successfully"
    }

    with patch(
        "cli.requests.delete",
        return_value=mock_response
    ):

        cli.delete_product(1)

    output = capsys.readouterr().out

    assert "Product deleted successfully" in output


def test_lookup_product(capsys):
    mock_response = Mock()

    mock_response.status_code = 200

    mock_response.json.return_value = {
        "product_name": "Test Chocolate",
        "brands": "Test Brand",
        "barcode": "123456",
        "ingredients_text": "Sugar, cocoa",
        "categories": "Snacks",
        "image_url": ""
    }

    with patch(
        "cli.requests.get",
        return_value=mock_response
    ):

        cli.lookup_product("123456")

    output = capsys.readouterr().out

    assert "Test Chocolate" in output
    assert "Test Brand" in output


def test_search_products(capsys):
    mock_response = Mock()

    mock_response.status_code = 200

    mock_response.json.return_value = {
        "count": 1,
        "products": [
            {
                "product_name": "Test Milk",
                "brands": "Test Brand",
                "barcode": "123456"
            }
        ]
    }

    with patch(
        "cli.requests.get",
        return_value=mock_response
    ):

        cli.search_products("milk")

    output = capsys.readouterr().out

    assert "Test Milk" in output


def test_import_product(capsys):
    mock_response = Mock()

    mock_response.status_code = 201

    mock_response.json.return_value = {
        "id": 4,
        "product_name": "Test Product",
        "price": 500,
        "stock": 20
    }

    args = Mock()

    args.barcode = "123456"
    args.price = 500
    args.stock = 20

    with patch(
        "cli.requests.post",
        return_value=mock_response
    ):

        cli.import_product(args)

    output = capsys.readouterr().out

    assert "Product imported successfully" in output

