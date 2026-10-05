
import argparse
import requests


BASE_URL = "http://127.0.0.1:5000"


def list_inventory():
    response = requests.get(f"{BASE_URL}/inventory")

    if response.status_code != 200:
        print("Error getting inventory")
        return

    products = response.json()

    if not products:
        print("Inventory is empty")
        return

    for product in products:
        print(
            f'ID: {product["id"]} | '
            f'Name: {product["product_name"]} | '
            f'Brand: {product["brands"]} | '
            f'Price: {product["price"]} | '
            f'Stock: {product["stock"]}'
        )


def get_product(item_id):
    response = requests.get(f"{BASE_URL}/inventory/{item_id}")

    if response.status_code == 404:
        print("Product not found")
        return

    if response.status_code != 200:
        print("Error getting product")
        return

    product = response.json()

    print(f'ID: {product["id"]}')
    print(f'Name: {product["product_name"]}')
    print(f'Brand: {product["brands"]}')
    print(f'Barcode: {product["barcode"]}')
    print(f'Price: {product["price"]}')
    print(f'Stock: {product["stock"]}')
    print(f'Ingredients: {product["ingredients_text"]}')
    print(f'Categories: {product["categories"]}')


def add_product(args):
    data = {
        "product_name": args.name,
        "brands": args.brand,
        "price": args.price,
        "stock": args.stock,
        "barcode": args.barcode
    }

    response = requests.post(
        f"{BASE_URL}/inventory",
        json=data
    )

    if response.status_code == 201:
        print("Product added successfully")
        print(response.json())
        return

    print(response.json().get("error", "Unable to add product"))


def update_product(args):
    data = {}

    if args.price is not None:
        data["price"] = args.price

    if args.stock is not None:
        data["stock"] = args.stock

    if args.name is not None:
        data["product_name"] = args.name

    if not data:
        print("Provide at least one value to update")
        return

    response = requests.patch(
        f"{BASE_URL}/inventory/{args.id}",
        json=data
    )

    if response.status_code == 200:
        print("Product updated successfully")
        print(response.json())
        return

    print(response.json().get("error", "Unable to update product"))


def delete_product(item_id):
    response = requests.delete(
        f"{BASE_URL}/inventory/{item_id}"
    )

    if response.status_code == 200:
        print("Product deleted successfully")
        return

    print(response.json().get("error", "Unable to delete product"))


def lookup_product(barcode):
    response = requests.get(
        f"{BASE_URL}/products/barcode/{barcode}"
    )

    if response.status_code == 200:
        product = response.json()

        print(f'Name: {product["product_name"]}')
        print(f'Brand: {product["brands"]}')
        print(f'Barcode: {product["barcode"]}')
        print(f'Ingredients: {product["ingredients_text"]}')
        print(f'Categories: {product["categories"]}')
        print(f'Image: {product["image_url"]}')
        return

    print(response.json().get("error", "Unable to find product"))


def search_products(name):
    response = requests.get(
        f"{BASE_URL}/products/search",
        params={"name": name}
    )

    if response.status_code != 200:
        print(response.json().get("error", "Unable to search products"))
        return

    data = response.json()

    if data["count"] == 0:
        print("No products found")
        return

    for product in data["products"]:
        print(
            f'Name: {product["product_name"]} | '
            f'Brand: {product["brands"]} | '
            f'Barcode: {product["barcode"]}'
        )


def import_product(args):
    data = {
        "barcode": args.barcode,
        "price": args.price,
        "stock": args.stock
    }

    response = requests.post(
        f"{BASE_URL}/products/import",
        json=data
    )

    if response.status_code == 201:
        print("Product imported successfully")
        print(response.json())
        return

    print(response.json().get("error", "Unable to import product"))


def main():
    parser = argparse.ArgumentParser(
        description="Inventory Management CLI"
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True
    )

    list_parser = subparsers.add_parser(
        "list",
        help="View all inventory"
    )
    list_parser.set_defaults(func=lambda args: list_inventory())

    get_parser = subparsers.add_parser(
        "get",
        help="View one inventory item"
    )
    get_parser.add_argument(
        "id",
        type=int
    )
    get_parser.set_defaults(
        func=lambda args: get_product(args.id)
    )

    add_parser = subparsers.add_parser(
        "add",
        help="Add a product"
    )
    add_parser.add_argument(
        "--name",
        required=True
    )
    add_parser.add_argument(
        "--brand",
        default=""
    )
    add_parser.add_argument(
        "--barcode",
        default=""
    )
    add_parser.add_argument(
        "--price",
        required=True,
        type=float
    )
    add_parser.add_argument(
        "--stock",
        required=True,
        type=int
    )
    add_parser.set_defaults(func=add_product)

    update_parser = subparsers.add_parser(
        "update",
        help="Update a product"
    )
    update_parser.add_argument(
        "id",
        type=int
    )
    update_parser.add_argument(
        "--name"
    )
    update_parser.add_argument(
        "--price",
        type=float
    )
    update_parser.add_argument(
        "--stock",
        type=int
    )
    update_parser.set_defaults(func=update_product)

    delete_parser = subparsers.add_parser(
        "delete",
        help="Delete a product"
    )
    delete_parser.add_argument(
        "id",
        type=int
    )
    delete_parser.set_defaults(
        func=lambda args: delete_product(args.id)
    )

    lookup_parser = subparsers.add_parser(
        "lookup",
        help="Find a product on OpenFoodFacts by barcode"
    )
    lookup_parser.add_argument(
        "barcode"
    )
    lookup_parser.set_defaults(
        func=lambda args: lookup_product(args.barcode)
    )

    search_parser = subparsers.add_parser(
        "search",
        help="Search OpenFoodFacts by product name"
    )
    search_parser.add_argument(
        "name"
    )
    search_parser.set_defaults(
        func=lambda args: search_products(args.name)
    )

    import_parser = subparsers.add_parser(
        "import",
        help="Import a product from OpenFoodFacts"
    )
    import_parser.add_argument(
        "barcode"
    )
    import_parser.add_argument(
        "--price",
        required=True,
        type=float
    )
    import_parser.add_argument(
        "--stock",
        required=True,
        type=int
    )
    import_parser.set_defaults(func=import_product)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()

