import copy
import random
from datetime import datetime

TIMESTAMP_FORMATS = ["%d/%m/%Y %H:%M", "%Y/%m/%d %H:%M:%S", "%Y-%m-%d %H:%M:%S", "%d-%m-%Y %H.%M"]
PAYMENT_VARIANTS = {
    "card": ["Card", "CARD", " card", "kort", "Kort"],
    "swish": ["Swish", "SWISH", "swish "],
    "cash": ["Cash", "kontant", "Kontanter"],
}


def _hit(rng: random.Random, share: float) -> bool:
    """True with probability `share`."""
    return rng.random() < share


def mess_up_timestamp(tx: dict, rng: random.Random, share: float) -> None:
    """Write the timestamp in another format, without time zone."""
    if _hit(rng, share):
        ts = datetime.fromisoformat(tx["transaction_timestamp"])
        tx["transaction_timestamp"] = ts.strftime(rng.choice(TIMESTAMP_FORMATS))


def mess_up_payment_method(tx: dict, rng: random.Random, share: float) -> None:
    """Mix upper/lower case, Swedish words, extra spaces or a missing value."""
    if _hit(rng, share):
        variants = PAYMENT_VARIANTS[tx["payment_method"]] + [None]
        tx["payment_method"] = rng.choice(variants)


def mess_up_header(tx: dict, rng: random.Random, share: float) -> None:
    """Small errors in the transaction header."""
    if _hit(rng, share):
        field = rng.choice(["currency", "campaign_code", "store_id", "customer_id"])
        if field == "currency":
            tx["currency"] = rng.choice(["sek", "kr", None])
        elif field == "campaign_code" and tx["campaign_code"]:
            tx["campaign_code"] = tx["campaign_code"].lower()
        elif field == "store_id":
            tx["store_id"] = rng.choice(["sto-001", "STO001", ""])
        elif field == "customer_id" and tx["customer_id"]:
            tx["customer_id"] = tx["customer_id"].replace("CUST-", "")


def mess_up_item(item: dict, rng: random.Random, share: float) -> None:
    """Errors on a receipt line: product id, price as text, odd quantity or missing value."""
    if not _hit(rng, share):
        return
    error = rng.choice(["product_id", "price", "quantity", "missing"])
    if error == "product_id":
        pid = item["product_id"]
        item["product_id"] = rng.choice([pid.lower(), f" {pid} ", pid.replace("PRD-", ""), "PRD-99999"])
    elif error == "price":
        price = f"{item['unit_price']:.2f}"
        item["unit_price"] = rng.choice([price.replace(".", ","), f"{price} kr", price])
    elif error == "quantity":
        item["quantity"] = rng.choice([0, 100])
    else:
        item[rng.choice(["discount_amount", "vat_rate"])] = None


def mess_up_totals(tx: dict, rng: random.Random, share: float) -> None:
    """Make the totals not match the lines, as after a register bug."""
    if _hit(rng, share):
        tx["total_amount"] = round(tx["total_amount"] + rng.choice([-10, 1, 100]), 2)


def make_dirty(transactions: list[dict], seed: int | None = 42, level: float = 1.0) -> list[dict]:
    """Return a dirty copy of the transactions. level scales how much dirt there is."""
    rng = random.Random(seed)
    dirty = []
    for original in transactions:
        tx = copy.deepcopy(original)
        mess_up_timestamp(tx, rng, 0.03 * level)
        mess_up_payment_method(tx, rng, 0.05 * level)
        mess_up_header(tx, rng, 0.03 * level)
        mess_up_totals(tx, rng, 0.005 * level)
        for item in tx["items"]:
            mess_up_item(item, rng, 0.02 * level)
        dirty.append(tx)
        if _hit(rng, 0.01 * level):
            dirty.append(copy.deepcopy(tx))  # sent twice by the register
    return dirty