from flask import Flask, request, jsonify
import requests

from data.inventory import inventory


app = Flask(__name__)

OPENFOODFACTS_PRODUCT_URL = "https://world.openfoodfacts.org/api/v3/product"
OPENFOODFACTS_SEARCH_URL = "https://world.openfoodfacts.org/cgi/search.pl"

HEADERS = {
    "User-Agent": "InventoryManagementSystem/1.0 (Moringa School Student Project)"
}


def get_next_id():
    if not inventory:
        return 1

    return max(item["id"] for item in inventory) + 1


def find_item(item_id):
    for item in inventory:
        if item["id"] == item_id:
            return item

    return None


def validate_product(data):
    if not data:
        return "Request body is required"

    if not data.get("product_name"):
        return "product_name is required"

    if "price" not in data:
        return "price is required"

    if "stock" not in data:
        return "stock is required"

    if not isinstance(data["price"], (int, float)):
        return "price must be a number"

    if data["price"] < 0:
        return "price cannot be negative"

    if not isinstance(data["stock"], int):
        return "stock must be an integer"

    if data["stock"] < 0:
        return "stock cannot be negative"

    return None


def get_product_from_openfoodfacts(barcode):
    url = f"{OPENFOODFACTS_PRODUCT_URL}/{barcode}"

    response = requests.get(
        url,
        headers=HEADERS,
        timeout=10
    )

    if response.status_code == 404:
        return None

    response.raise_for_status()

    data = response.json()

    if data.get("status") not in [1, "1"]:
        return None

    product = data.get("product", {})

    return {
        "product_name": product.get("product_name", ""),
        "brands": product.get("brands", ""),
        "barcode": barcode,
        "ingredients_text": product.get("ingredients_text", ""),
        "categories": product.get("categories", ""),
        "image_url": product.get("image_url", "")
    }


def search_openfoodfacts_by_name(name):
    params = {
        "search_terms": name,
        "search_simple": 1,
        "action": "process",
        "json": 1,
        "page_size": 10
    }

    response = requests.get(
        OPENFOODFACTS_SEARCH_URL,
        params=params,
        headers=HEADERS,
        timeout=10
    )

    response.raise_for_status()

    data = response.json()

    products = []

    for product in data.get("products", []):
        products.append({
            "product_name": product.get("product_name", ""),
            "brands": product.get("brands", ""),
            "barcode": product.get("code", ""),
            "ingredients_text": product.get("ingredients_text", ""),
            "categories": product.get("categories", ""),
            "image_url": product.get("image_url", "")
        })

    return products


@app.route("/")
def home():
    return jsonify({
        "message": "Inventory Management API",
        "version": "1.0"
    }), 200


@app.route("/inventory", methods=["GET"])
def get_inventory():
    return jsonify(inventory), 200


@app.route("/inventory/<int:item_id>", methods=["GET"])
def get_inventory_item(item_id):
    item = find_item(item_id)

    if item is None:
        return jsonify({
            "error": "Inventory item not found"
        }), 404

    return jsonify(item), 200


@app.route("/inventory", methods=["POST"])
def add_inventory_item():
    data = request.get_json(silent=True)

    error = validate_product(data)

    if error:
        return jsonify({
            "error": error
        }), 400

    new_item = {
        "id": get_next_id(),
        "product_name": data["product_name"],
        "brands": data.get("brands", ""),
        "barcode": data.get("barcode", ""),
        "price": data["price"],
        "stock": data["stock"],
        "ingredients_text": data.get("ingredients_text", ""),
        "categories": data.get("categories", ""),
        "image_url": data.get("image_url", "")
    }

    inventory.append(new_item)

    return jsonify(new_item), 201


@app.route("/inventory/<int:item_id>", methods=["PATCH"])
def update_inventory_item(item_id):
    item = find_item(item_id)

    if item is None:
        return jsonify({
            "error": "Inventory item not found"
        }), 404

    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "error": "Request body is required"
        }), 400

    if "price" in data:
        if not isinstance(data["price"], (int, float)):
            return jsonify({
                "error": "price must be a number"
            }), 400

        if data["price"] < 0:
            return jsonify({
                "error": "price cannot be negative"
            }), 400

        item["price"] = data["price"]

    if "stock" in data:
        if not isinstance(data["stock"], int):
            return jsonify({
                "error": "stock must be an integer"
            }), 400

        if data["stock"] < 0:
            return jsonify({
                "error": "stock cannot be negative"
            }), 400

        item["stock"] = data["stock"]

    if "product_name" in data:
        if not data["product_name"]:
            return jsonify({
                "error": "product_name cannot be empty"
            }), 400

        item["product_name"] = data["product_name"]

    if "brands" in data:
        item["brands"] = data["brands"]

    if "barcode" in data:
        item["barcode"] = data["barcode"]

    if "ingredients_text" in data:
        item["ingredients_text"] = data["ingredients_text"]

    if "categories" in data:
        item["categories"] = data["categories"]

    if "image_url" in data:
        item["image_url"] = data["image_url"]

    return jsonify(item), 200


@app.route("/inventory/<int:item_id>", methods=["DELETE"])
def delete_inventory_item(item_id):
    item = find_item(item_id)

    if item is None:
        return jsonify({
            "error": "Inventory item not found"
        }), 404

    inventory.remove(item)

    return jsonify({
        "message": "Inventory item deleted successfully"
    }), 200


@app.route("/products/barcode/<barcode>", methods=["GET"])
def get_external_product(barcode):
    try:
        product = get_product_from_openfoodfacts(barcode)

        if product is None:
            return jsonify({
                "error": "Product not found on OpenFoodFacts"
            }), 404

        return jsonify(product), 200

    except requests.RequestException:
        return jsonify({
            "error": "Unable to connect to OpenFoodFacts"
        }), 503


@app.route("/products/search", methods=["GET"])
def search_external_products():
    name = request.args.get("name", "").strip()

    if not name:
        return jsonify({
            "error": "name query parameter is required"
        }), 400

    try:
        products = search_openfoodfacts_by_name(name)

        return jsonify({
            "count": len(products),
            "products": products
        }), 200

    except requests.RequestException:
        return jsonify({
            "error": "Unable to connect to OpenFoodFacts"
        }), 503


@app.route("/products/import", methods=["POST"])
def import_product():
    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "error": "Request body is required"
        }), 400

    barcode = data.get("barcode")

    if not barcode:
        return jsonify({
            "error": "barcode is required"
        }), 400

    if "price" not in data:
        return jsonify({
            "error": "price is required"
        }), 400

    if "stock" not in data:
        return jsonify({
            "error": "stock is required"
        }), 400

    if not isinstance(data["price"], (int, float)):
        return jsonify({
            "error": "price must be a number"
        }), 400

    if data["price"] < 0:
        return jsonify({
            "error": "price cannot be negative"
        }), 400

    if not isinstance(data["stock"], int):
        return jsonify({
            "error": "stock must be an integer"
        }), 400

    if data["stock"] < 0:
        return jsonify({
            "error": "stock cannot be negative"
        }), 400

    try:
        product = get_product_from_openfoodfacts(barcode)

        if product is None:
            return jsonify({
                "error": "Product not found on OpenFoodFacts"
            }), 404

        product["id"] = get_next_id()
        product["price"] = data["price"]
        product["stock"] = data["stock"]

        inventory.append(product)

        return jsonify(product), 201

    except requests.RequestException:
        return jsonify({
            "error": "Unable to connect to OpenFoodFacts"
        }), 503


if __name__ == "__main__":
    app.run(debug=True)