import pandas as pd
from typing import Dict, Tuple


def save_to_excel(
    dfs: Dict[str, pd.DataFrame], file_name: str, subfolder="/app/results/"
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

    with pd.ExcelWriter(f"{subfolder}{file_name}.xlsx") as writer:
        for sheet, df in dfs.items():
            df.to_excel(writer, sheet_name=sheet, index=False)
