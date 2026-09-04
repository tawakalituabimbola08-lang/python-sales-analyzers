import pandas as pd

FILE = "sample_sales.csv"


def get_currency():
    while True:
        currency = input(
            "Enter 3-letter currency code (e.g. NGN, USD, EUR): "
        ).strip().upper()

        if len(currency) == 3 and currency.isalpha():
            return currency

        print("Invalid currency code. Please enter 3 letters.")


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
        print("Error: CSV must contain:")
        print("product, quantity, price")
        return None

    # Convert quantity and price to numbers
    try:
        data["quantity"] = pd.to_numeric(data["quantity"])
        data["price"] = pd.to_numeric(data["price"])
    except ValueError:
        print("Error: quantity and price must contain numbers.")
        return None

    # If currency column doesn't exist, ask the user
    if "currency" not in data.columns:
        currency = get_currency()
        data["currency"] = currency

    else:
        # Clean currency codes
        data["currency"] = (
            data["currency"]
            .astype(str)
            .str.strip()
            .str.upper()
        )

    # Calculate revenue
    data["revenue"] = data["quantity"] * data["price"]

    return data


def show_summary(data):
    print("\n===== SALES SUMMARY =====")

    for currency, group in data.groupby("currency"):
        total_revenue = group["revenue"].sum()
        total_units = group["quantity"].sum()

        print(f"\nCurrency: {currency}")
        print(f"Total revenue: {total_revenue:,.2f} {currency}")
        print(f"Total units: {total_units}")


def show_best_product(data):
    print("\n===== BEST-SELLING PRODUCTS =====")

    for currency, group in data.groupby("currency"):
        product = group.loc[
            group["quantity"].idxmax(), "product"
        ]

        quantity = group["quantity"].max()

        print(f"{currency}: {product} ({quantity} units)")


def show_highest_revenue(data):
    print("\n===== HIGHEST REVENUE PRODUCTS =====")

    for currency, group in data.groupby("currency"):
        product = group.loc[
            group["revenue"].idxmax(), "product"
        ]

        revenue = group["revenue"].max()

        print(f"{currency}: {product} ({revenue:,.2f} {currency})")


def show_all_products(data):
    print("\n===== ALL PRODUCTS =====")
    print(data.to_string(index=False))


def main():
    data = load_data()

    if data is None:
        return

    while True:
        print("\n===== PYTHON SALES ANALYZER =====")
        print("1. Sales summary")
        print("2. Best-selling products")
        print("3. Highest revenue products")
        print("4. All products")
        print("5. Exit")

        choice = input("\nChoose an option: ").strip()

        if choice == "1":
            show_summary(data)

        elif choice == "2":
            show_best_product(data)

        elif choice == "3":
            show_highest_revenue(data)

        elif choice == "4":
            show_all_products(data)

        elif choice == "5":
            print("Goodbye!")
            break

        else:
            print("Invalid choice. Please choose 1-5.")


if __name__ == "__main__":
    main()