import numpy as np

from ._common import load_sales


def perform_xyz(
    csv_path="/app/data/sales.csv",
    product_col="product_id",
    price_col="product_price",
    units_col="quantity",
):
    # Load the data
    df = load_sales(csv_path, product_col, price_col, units_col)

    # Calculate the Coefficient of Variation (CV) for each product
    product_variation = (
        df.groupby(product_col)["sales"]
        .apply(
            lambda x: (
                (x / x.max()).std(ddof=0) / (x / x.max()).mean()
                if x.max() > 0
                else float("nan")
            )
        )
        .reset_index()
    )
    product_variation.columns = [product_col, "cv"]

    # Sort by cv in ascending order
    product_variation = product_variation.sort_values(by="cv", ascending=True)

    # Define thresholds (in this case, we divide into three equal parts)
    finite_cv = product_variation["cv"].dropna()
    thresholds = np.percentile(finite_cv, [33, 66]) if len(finite_cv) else [0, 0]

    # Assign XYZ categories
    product_variation["category"] = "Z"
    product_variation.loc[product_variation["cv"] <= thresholds[1], "category"] = "Y"
    product_variation.loc[product_variation["cv"] <= thresholds[0], "category"] = "X"

    # Calculate statistics for each category
    xyz_result = (
        product_variation.groupby("category")
        .agg({product_col: "count", "cv": "mean"})
        .reset_index()
    )
    xyz_result = xyz_result.rename(
        columns={
            product_col: "number_of_products",
            "cv": "average_cv",
        },
    )

    result = {"XYZ stats": xyz_result, "XYZ classification": product_variation}

    return result
