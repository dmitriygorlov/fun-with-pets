import pandas as pd
import numpy as np
from scipy.stats.mstats import variation


def perform_xyz(
    csv_path="/app/data/sales.csv",
    product_col="product_id",
    price_col="product_price",
    units_col="quantity",
):
    # Load the data
    df = pd.read_csv(csv_path)

    # Calculate sales for each product
    df["sales"] = df[price_col] * df[units_col]

    # Calculate the Coefficient of Variation (CV) for each product
    product_variation = (
        df.groupby(product_col)["sales"].apply(lambda x: variation(x)).reset_index()
    )
    product_variation.columns = [product_col, "cv"]

    # Sort by cv in ascending order
    product_variation.sort_values(by="cv", ascending=True, inplace=True)

    # Define thresholds (in this case, we divide into three equal parts)
    thresholds = np.percentile(product_variation["cv"], [33, 66])

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
    xyz_result.rename(
        columns={
            product_col: "number_of_products",
            "cv": "average_cv",
        },
        inplace=True,
    )

    result = {"XYZ stats": xyz_result, "XYZ classification": product_variation}

    return result
