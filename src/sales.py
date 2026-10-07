from collections import OrderedDict
from datetime import date, datetime, time, timedelta
from pathlib import Path

import pandas as pd
from faker import Faker

OPENING_TIME = time(10, 0)
CLOSING_TIME = time(19, 0)
PAYMENT_METHODS = OrderedDict([("card", 0.70), ("swish", 0.25), ("cash", 0.05)])
DISCOUNTS = OrderedDict([(0, 0.85), (10, 0.10), (20, 0.05)])


def create_faker(seed: int = 42) -> Faker:
    """Create a seeded Faker instance so the data is the same every run."""
    fake = Faker("sv_SE")
    Faker.seed(seed)
    return fake


def generate_receipt(fake: Faker, products: pd.DataFrame, receipt_id: str, sold_at: datetime) -> list[dict]:
    """Create one receipt with 1-4 different products. Returns one row per product."""
    n_items = fake.random_int(min=1, max=4)
    chosen = fake.random_elements(elements=products.to_dict("records"), length=n_items, unique=True)
    payment_method = fake.random_element(elements=PAYMENT_METHODS)

    rows = []
    for product in chosen:
        rows.append({
            "receipt_id": receipt_id,
            "sold_at": sold_at,
            "product_id": product["product_id"],
            "quantity": fake.random_int(min=1, max=3),
            "unit_price": product["price_sek"],
            "discount_pct": fake.random_element(elements=DISCOUNTS),
            "payment_method": payment_method,
        })
    return rows


def generate_day(fake: Faker, products: pd.DataFrame, day: date, start_number: int) -> list[dict]:
    """Create all receipts for one day. More customers on weekends."""
    is_weekend = day.weekday() >= 5
    n_receipts = fake.random_int(min=40, max=80) if is_weekend else fake.random_int(min=20, max=50)

    opening = datetime.combine(day, OPENING_TIME)
    closing = datetime.combine(day, CLOSING_TIME)
    times = sorted(
        fake.date_time_between_dates(opening, closing).replace(microsecond=0) for _ in range(n_receipts)
    )

    rows = []
    for i, sold_at in enumerate(times):
        receipt_id = f"R{sold_at:%Y%m%d%H%M%S}{fake.random_int(100, 999)}"
        rows.extend(generate_receipt(fake, products, receipt_id, sold_at))
    return rows


def generate_sales(products: pd.DataFrame, start_date: date, end_date: date, seed: int = 42) -> pd.DataFrame:
    """Create sales for every day between start_date and end_date."""
    fake = create_faker(seed)
    rows = []
    next_receipt = 1
    day = start_date
    while day <= end_date:
        day_rows = generate_day(fake, products, day, start_number=next_receipt)
        next_receipt += len({row["receipt_id"] for row in day_rows})
        rows.extend(day_rows)
        day += timedelta(days=1)
    return pd.DataFrame(rows)


def save_to_csv(df: pd.DataFrame, filename: str, folder: str = "data") -> None:
    """Save a DataFrame as CSV in the data folder."""
    Path(folder).mkdir(exist_ok=True)
    df.to_csv(Path(folder) / filename, index=False)