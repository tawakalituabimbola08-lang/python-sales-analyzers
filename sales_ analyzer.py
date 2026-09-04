import pandas as pd

FILE = "sample_sales.csv"


def load_data():
    try:
        data = pd.read_csv(FILE)
    except FileNotFoundError:
        print(f"Error: {FILE} was not found.")
        return None
    except Exception as error:
        print("Error reading CSV:", error)
        return None

    required_columns = {"product", "quantity", "price"}

    if not required_columns.issubset(data.columns):
        print("Error: CSV must contain product, quantity, and price columns.")
        return None

    return data


def analyze_sales(data):
    try:
        data["quantity"] = pd.to_numeric(data["quantity"])
        data["price"] = pd.to_numeric(data["price"])
    except ValueError:
        print("Error: quantity and price must contain numbers.")
        return

    data["revenue"] = data["quantity"] * data["price"]

    total_revenue = data["revenue"].sum()
    total_units = data["quantity"].sum()

    best_selling = data.loc[data["quantity"].idxmax(), "product"]
    highest_revenue = data.loc[data["revenue"].idxmax(), "product"]

    print("\n===== SALES REPORT =====")
    print(f"Total revenue: ₦{total_revenue:,.2f}")
    print(f"Total units sold: {total_units}")
    print(f"Best-selling product: {best_selling}")
    print(f"Highest revenue product: {highest_revenue}")

    print("\n===== PRODUCT DETAILS =====")
    print(data.to_string(index=False))


def main():
    data = load_data()

    if data is not None:
        analyze_sales(data)


if __name__ == "__main__":
    main()