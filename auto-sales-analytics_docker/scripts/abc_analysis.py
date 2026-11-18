import math

from ._common import load_sales


def perform_abc(
    csv_path="/app/data/sales.csv",
    product_col="product_id",
    price_col="product_price",
    units_col="quantity",
):
    # Load the data
    df = load_sales(csv_path, product_col, price_col, units_col)

    # Calculate total sales for each product
    product_sales = df.groupby(product_col)["sales"].sum().reset_index()

    # Sort by sales in descending order
    product_sales = product_sales.sort_values(by="sales", ascending=False)

    # Calculate cumulative sales
    product_sales["cumulative_sales"] = product_sales["sales"].cumsum()

    # Calculate total sales and percentage of cumulative sales
    total_sales = product_sales["sales"].sum()
    if not math.isfinite(total_sales) or total_sales <= 0:
        raise ValueError("ABC requires finite positive total revenue")
    product_sales["cumulative_percent"] = 100 * (
        product_sales["cumulative_sales"] / total_sales
    )

    # Assign ABC categories
    product_sales["category"] = "C"
    product_sales.loc[product_sales["cumulative_percent"] <= 80, "category"] = "A"
    product_sales.loc[
        (product_sales["cumulative_percent"] > 80)
        & (product_sales["cumulative_percent"] <= 95),
        "category",
    ] = "B"

    # Calculate statistics for each category
    abc_result = (
        product_sales.groupby("category").agg({product_col: "count", "sales": "sum"})
    ).reset_index()
    abc_result = abc_result.rename(
        columns={
            product_col: "number_of_products",
            "sales": "total_sales",
        },
    )

    result = {"ABC stats": abc_result, "ABC classification": product_sales}

    return result
