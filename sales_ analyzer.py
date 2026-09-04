import re
import pandas as pd
from babel.numbers import get_currency_symbol, get_currency_name

FILE = "sample_sales.csv"


COLUMN_ALIASES = {
    "date": [
        "date",
        "sale_date",
        "transaction_date",
        "order_date"
    ],
    "product": [
        "product",
        "product_name",
        "item",
        "item_name",
        "name"
    ],
    "quantity": [
        "quantity",
        "qty",
        "units",
        "units_sold",
        "amount_sold"
    ],
    "price": [
        "price",
        "unit_price",
        "selling_price",
        "cost",
        "unit_cost"
    ],
    "currency": [
        "currency",
        "currency_code",
        "curr",
        "money"
    ]
}


def normalize_column_name(name):
    return (
        str(name)
        .strip()
        .lower()
        .replace(" ", "_")
        .replace("-", "_")
    )


def detect_columns(data):
    data.columns = [
        normalize_column_name(column)
        for column in data.columns
    ]

    detected = {}

    for standard_name, aliases in COLUMN_ALIASES.items():

        aliases = [
            normalize_column_name(alias)
            for alias in aliases
        ]

        for column in data.columns:
            if column in aliases:
                detected[standard_name] = column
                break

    return detected


def clean_money(value):
    """Turn values such as ₦450,000 or $500 into numbers."""

    if pd.isna(value):
        return None

    value = str(value).strip()

    # Keep digits, decimal point, minus sign and comma
    value = re.sub(r"[^\d.,\-]", "", value)

    # Remove thousands separators
    value = value.replace(",", "")

    try:
        return float(value)
    except ValueError:
        return None


def get_currency():
    """Ask user for currency when CSV has no currency column."""

    while True:

        currency = input(
            "\nEnter 3-letter currency code "
            "(NGN, USD, EUR, GBP): "
        ).strip().upper()

        if len(currency) != 3 or not currency.isalpha():
            print("Please enter exactly 3 letters.")
            continue

        try:
            symbol = get_currency_symbol(
                currency,
                locale="en_US"
            )

            name = get_currency_name(
                currency,
                locale="en_US"
            )

            print(f"Currency: {name}")
            print(f"Symbol: {symbol}")

            return currency

        except Exception:
            print("Unknown currency code. Try again.")


def get_date_format():
    """Ask how dates are written."""

    print("\n===== DATE FORMAT =====")
    print("1. DD/MM/YYYY")
    print("2. MM/DD/YYYY")
    print("3. YYYY-MM-DD")

    while True:

        choice = input("Choose date format: ").strip()

        if choice == "1":
            return True

        elif choice == "2":
            return False

        elif choice == "3":
            return None

        else:
            print("Please choose 1, 2 or 3.")


def load_data():

    try:
        data = pd.read_csv(FILE)

    except FileNotFoundError:
        print(f"Error: {FILE} was not found.")
        return None

    except Exception as error:
        print("Error reading CSV:", error)
        return None

    columns = detect_columns(data)

    # Required columns
    required = ["product", "quantity", "price"]

    for column in required:

        if column not in columns:
            print(
                f"Could not find a {column} column."
            )
            return None

    # Rename columns
    rename_map = {
        columns["product"]: "product",
        columns["quantity"]: "quantity",
        columns["price"]: "price"
    }

    data = data.rename(columns=rename_map)

    # Clean numbers
    data["quantity"] = data["quantity"].apply(
        clean_money
    )

    data["price"] = data["price"].apply(
        clean_money
    )

    if data["quantity"].isna().any():
        print("Error: some quantities are invalid.")
        return None

    if data["price"].isna().any():
        print("Error: some prices are invalid.")
        return None

    # Currency
    if "currency" in columns:

        currency_column = columns["currency"]

        data["currency"] = (
            data[currency_column]
            .astype(str)
            .str.strip()
            .str.upper()
        )

    else:

        print("\nNo currency column found.")

        currency = get_currency()

        data["currency"] = currency

    # Date
    if "date" in columns:

        date_column = columns["date"]

        date_format = get_date_format()

        if date_format is True:

            data["date"] = pd.to_datetime(
                data[date_column],
                dayfirst=True,
                errors="coerce"
            )

        elif date_format is False:

            data["date"] = pd.to_datetime(
                data[date_column],
                dayfirst=False,
                errors="coerce"
            )

        else:

            data["date"] = pd.to_datetime(
                data[date_column],
                errors="coerce"
            )

        if data["date"].isna().any():
            print(
                "Error: some dates could not be understood."
            )
            return None

    else:

        print(
            "\nNo date column found."
            "\nTime-based analysis will be unavailable."
        )

        data["date"] = pd.NaT

    # Revenue
    data["revenue"] = (
        data["quantity"] *
        data["price"]
    )

    return data


def show_summary(data):

    print("\n===== SALES SUMMARY =====")

    for currency, group in data.groupby("currency"):

        symbol = get_currency_symbol(
            currency,
            locale="en_US"
        )

        revenue = group["revenue"].sum()
        units = group["quantity"].sum()

        print(f"\nCurrency: {currency} ({symbol})")
        print(
            f"Total revenue: "
            f"{symbol}{revenue:,.2f}"
        )
        print(f"Total units: {units}")


def show_best_product(data):

    print("\n===== BEST-SELLING PRODUCTS =====")

    for currency, group in data.groupby("currency"):

        product = group.loc[
            group["quantity"].idxmax(),
            "product"
        ]

        quantity = group["quantity"].max()

        print(
            f"{currency}: "
            f"{product} "
            f"({quantity:g} units)"
        )


def show_highest_revenue(data):

    print(
        "\n===== HIGHEST REVENUE PRODUCTS ====="
    )

    for currency, group in data.groupby("currency"):

        symbol = get_currency_symbol(
            currency,
            locale="en_US"
        )

        product = group.loc[
            group["revenue"].idxmax(),
            "product"
        ]

        revenue = group["revenue"].max()

        print(
            f"{currency}: "
            f"{product} "
            f"({symbol}{revenue:,.2f})"
        )


def show_monthly_sales(data):

    if data["date"].isna().all():

        print("No date data available.")
        return

    print("\n===== MONTHLY SALES =====")

    data = data.copy()

    data["month"] = data["date"].dt.to_period("M")

    monthly = (
        data.groupby(
            ["currency", "month"]
        )["revenue"]
        .sum()
    )

    for (currency, month), revenue in monthly.items():

        symbol = get_currency_symbol(
            currency,
            locale="en_US"
        )

        print(
            f"{month}: "
            f"{symbol}{revenue:,.2f} "
            f"({currency})"
        )


def show_all_products(data):

    print("\n===== ALL SALES =====")

    print(
        data.to_string(index=False)
    )


def main():

    data = load_data()

    if data is None:
        return

    while True:

        print(
            "\n===== PYTHON SALES ANALYZER ====="
        )

        print("1. Sales summary")
        print("2. Best-selling products")
        print("3. Highest revenue products")
        print("4. Monthly sales")
        print("5. Show all sales")
        print("6. Exit")

        choice = input(
            "\nChoose an option: "
        ).strip()

        if choice == "1":
            show_summary(data)

        elif choice == "2":
            show_best_product(data)

        elif choice == "3":
            show_highest_revenue(data)

        elif choice == "4":
            show_monthly_sales(data)

        elif choice == "5":
            show_all_products(data)

        elif choice == "6":
            print("Goodbye!")
            break

        else:
            print(
                "Invalid choice. "
                "Please choose 1-6."
            )


if __name__ == "__main__":
    main()