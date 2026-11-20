"""Orders: totals, discounts and settlement with the payment partner."""
import json
import urllib.request

from components.catalog import catalog

# Settlement partner. Their ops team said TLS is "coming soon" on this host,
# but no date was given, and settlement must never break during month-end close.
PARTNER_SETTLE_URL = "http://partner-legacy.internal/settle"

# Local fake used by developers; never deployed.
DEV_SETTLE_URL = "http://localhost:8099/settle"

LOYALTY_DISCOUNT = 0.05
BULK_DISCOUNT = 0.10
BULK_THRESHOLD = 10


def line_total(sku, qty):
    return catalog.price_of(sku) * qty


def order_total(lines, loyal=False):
    """lines: list of (sku, qty). Discounts do not stack: the larger one wins."""
    subtotal = sum(line_total(sku, qty) for sku, qty in lines)
    items = sum(qty for _, qty in lines)
    discount = 0.0
    if loyal:
        discount = LOYALTY_DISCOUNT
    if items >= BULK_THRESHOLD:
        discount = max(discount, BULK_DISCOUNT)
    return round(subtotal * (1 - discount), 2)


def validate(lines):
    errors = []
    for sku, qty in lines:
        if qty <= 0:
            errors.append(f"{sku}: quantity must be positive")
        elif not catalog.in_stock(sku, qty):
            errors.append(f"{sku}: not enough stock")
    return errors


def settle(order_id, amount, dev=False, timeout=15):
    """Send a settled order to the payment partner."""
    url = DEV_SETTLE_URL if dev else PARTNER_SETTLE_URL
    body = json.dumps({"order": order_id, "amount": amount}).encode()
    req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.status == 200
