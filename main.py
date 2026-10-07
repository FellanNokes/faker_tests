from datetime import date

from src.products import get_products
from src.sales import generate_sales, save_to_csv

products = get_products()
sales = generate_sales(products, start_date=date(2025, 1, 1), end_date=date(2025, 12, 31))

save_to_csv(products, "products.csv")
save_to_csv(sales, "sales.csv")