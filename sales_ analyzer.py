import pandas as pd

# Load sales data
data = pd.read_csv("sample_sales.csv")

# Calculate revenue for each product
data["revenue"] = data["quantity"] * data["price"]

# Business statistics
total_revenue = data["revenue"].sum()
total_units = data["quantity"].sum()

best_selling_product = data.loc[
    data["quantity"].idxmax(), "product"
]

highest_revenue_product = data.loc[
    data["revenue"].idxmax(), "product"
]

print("===== SALES REPORT =====")
print("Total revenue:", total_revenue)
print("Total units sold:", total_units)
print("Best-selling product:", best_selling_product)
print("Highest revenue product:", highest_revenue_product)

print("\n===== PRODUCT DETAILS =====")
print(data)