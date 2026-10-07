import random

import pandas as pd

DATE_FORMATS = ["%d/%m/%Y %H:%M", "%Y/%m/%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%d-%m-%Y %H.%M"]
PAYMENT_VARIANTS = {
    "card": ["Card", "CARD", " card", "kort", "Kort"],
    "swish": ["Swish", "SWISH", "swish "],
    "cash": ["Cash", "kontant", "Kontanter"],
}


def _pick_rows(df: pd.DataFrame, share: float, rng: random.Random) -> list:
    """Pick a random share of the row indexes."""
    n = int(len(df) * share)
    return rng.sample(list(df.index), n)


def mess_up_dates(df: pd.DataFrame, rng: random.Random, share: float = 0.03) -> pd.DataFrame:
    """Write some timestamps in other formats, as if they came from an older cash register."""
    df["sold_at"] = df["sold_at"].astype(str)
    for i in _pick_rows(df, share, rng):
        ts = pd.Timestamp(df.at[i, "sold_at"])
        df.at[i, "sold_at"] = ts.strftime(rng.choice(DATE_FORMATS))
    return df


def mess_up_prices(df: pd.DataFrame, rng: random.Random, share: float = 0.03) -> pd.DataFrame:
    """Use decimal comma or add ' kr' to some prices."""
    df["unit_price"] = df["unit_price"].map(lambda p: f"{p:.2f}")
    for i in _pick_rows(df, share, rng):
        price = df.at[i, "unit_price"]
        df.at[i, "unit_price"] = rng.choice([price.replace(".", ","), f"{price} kr", price.replace(".00", "")])
    return df


def mess_up_payment_methods(df: pd.DataFrame, rng: random.Random, share: float = 0.05) -> pd.DataFrame:
    """Mix upper/lower case, Swedish words and extra spaces."""
    for i in _pick_rows(df, share, rng):
        df.at[i, "payment_method"] = rng.choice(PAYMENT_VARIANTS[df.at[i, "payment_method"]])
    return df


def mess_up_product_ids(df: pd.DataFrame, rng: random.Random, share: float = 0.01) -> pd.DataFrame:
    """Lowercase, add spaces or use a product id that does not exist in the catalog."""
    for i in _pick_rows(df, share, rng):
        pid = df.at[i, "product_id"]
        df.at[i, "product_id"] = rng.choice([pid.lower(), f" {pid} ", "P9999"])
    return df


def add_missing_values(df: pd.DataFrame, rng: random.Random, share: float = 0.02) -> pd.DataFrame:
    """Blank out some discounts and payment methods."""
    df["discount_pct"] = df["discount_pct"].astype("object")
    for i in _pick_rows(df, share, rng):
        df.at[i, rng.choice(["discount_pct", "payment_method"])] = None
    return df


def add_bad_quantities(df: pd.DataFrame, rng: random.Random, share: float = 0.005) -> pd.DataFrame:
    """Add returns (negative), zero and typos like 100 instead of 1."""
    for i in _pick_rows(df, share, rng):
        df.at[i, "quantity"] = rng.choice([-1, -1, 0, 100])
    return df


def add_duplicates(df: pd.DataFrame, rng: random.Random, share: float = 0.01) -> pd.DataFrame:
    """Copy some rows, as if the register sent them twice."""
    duplicates = df.loc[_pick_rows(df, share, rng)]
    return pd.concat([df, duplicates]).sort_index(kind="stable").reset_index(drop=True)


def make_dirty(sales: pd.DataFrame, seed: int = 42) -> pd.DataFrame:
    """Return a dirty copy of the clean sales data."""
    rng = random.Random(seed)
    df = sales.copy()
    df = mess_up_dates(df, rng)
    df = mess_up_prices(df, rng)
    df = mess_up_payment_methods(df, rng)
    df = mess_up_product_ids(df, rng)
    df = add_missing_values(df, rng)
    df = add_bad_quantities(df, rng)
    df = add_duplicates(df, rng)
    return df