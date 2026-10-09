import pandas as pd
 
from src.dirty import make_dirty
from src.sales import generate_month
from src.storage import save_jsonl
 
 
def export_year(products: pd.DataFrame, year: int, folder: str = "data/sales") -> None:
    """Create one dirty JSON Lines file per month, e.g. sales_2025_01.jsonl."""
    for month in range(1, 13):
        transactions = generate_month(products, year, month)
        dirty = make_dirty(transactions, seed=year * 100 + month)
        save_jsonl(dirty, f"sales_{year}_{month:02d}.jsonl", folder)