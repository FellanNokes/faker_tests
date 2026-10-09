from src.export import export_year
from src.products import get_products
from src.storage import save_csv

products = get_products()

save_csv(products, "products.csv")
export_year(products, 2025)