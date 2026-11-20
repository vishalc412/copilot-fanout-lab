"""Product catalog: prices, stock and the nightly supplier feed."""
import json
import urllib.request

SUPPLIER_FEED_URL = "http://feeds.supplier-one.example.com/v2/products.json"
IMAGE_CDN = "https://cdn.example.com/img/"

_PRODUCTS = {
    "SKU-1": {"name": "Kettle", "price": 24.0, "stock": 12},
    "SKU-2": {"name": "Toaster", "price": 39.5, "stock": 0},
    "SKU-3": {"name": "Mug", "price": 6.0, "stock": 140},
}


def get_product(sku):
    """Return the product dict for a SKU, or None."""
    return _PRODUCTS.get(sku)


def price_of(sku):
    product = get_product(sku)
    if product is None:
        raise KeyError(f"unknown sku {sku}")
    return product["price"]


def in_stock(sku, qty=1):
    product = get_product(sku)
    return product is not None and product["stock"] >= qty


def image_url(sku):
    return IMAGE_CDN + sku.lower() + ".jpg"


def fetch_supplier_feed(timeout=10):
    """Pull the supplier's product feed. Runs nightly from cron."""
    with urllib.request.urlopen(SUPPLIER_FEED_URL, timeout=timeout) as resp:
        return json.loads(resp.read())


def apply_feed(feed):
    """Update prices and stock from a supplier feed."""
    for item in feed.get("products", []):
        if item["sku"] in _PRODUCTS:
            _PRODUCTS[item["sku"]]["price"] = float(item["price"])
            _PRODUCTS[item["sku"]]["stock"] = int(item["stock"])
