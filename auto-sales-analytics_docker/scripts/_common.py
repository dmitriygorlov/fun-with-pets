from pathlib import Path

import numpy as np
import pandas as pd


def save_to_excel(
    dfs: dict[str, pd.DataFrame], file_name: str, subfolder="/app/results/"
) -> None:
    """
    Save each DataFrame in dfs to a different sheet in the Excel file at file_path.

    Parameters
    ----------
    dfs: dict
        A dictionary where the key is the name of the sheet in the Excel file and
        the value is the DataFrame to save to that sheet.
    file_path: str
        The path to the Excel file.
    """

    Path(subfolder).mkdir(parents=True, exist_ok=True)
    with pd.ExcelWriter(Path(subfolder) / f"{file_name}.xlsx") as writer:
        for sheet, df in dfs.items():
            df.to_excel(writer, sheet_name=sheet, index=False)


def load_sales(csv_path, product_col, price_col, units_col):
    """Validate non-negative transaction revenue; returns/refunds need a separate policy."""
    df = pd.read_csv(csv_path)
    required = [product_col, price_col, units_col]
    if any(col not in df for col in required):
        raise ValueError("Missing required sales columns")
    if df.empty or df[required].isna().any().any():
        raise ValueError("Sales must contain complete transactions")
    for col in [price_col, units_col]:
        df[col] = pd.to_numeric(df[col], errors="raise").astype(float)
        if not np.isfinite(df[col]).all() or (df[col] < 0).any():
            raise ValueError("Prices and quantities must be finite and non-negative")
    df["sales"] = df[price_col] * df[units_col]
    if not np.isfinite(df["sales"]).all():
        raise ValueError("Revenue overflow")
    return df
