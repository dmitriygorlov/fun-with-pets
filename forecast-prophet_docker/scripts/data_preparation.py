import numpy as np
import pandas as pd


def prepare_data(file_path):
    """Read and preprocess data from CSV file.

    Assumes the first two columns are 'date' and 'sales'.
    Renames columns to 'ds' and 'y' for Prophet compatibility.
    Groups sales data by day if more detailed sales data is provided.
    """
    try:
        df = pd.read_csv(file_path, usecols=[0, 1])

        df.columns = ["ds", "y"]

        print("size of original data: ", df.shape)

        df["ds"] = pd.to_datetime(df["ds"])
        if df["ds"].dt.tz is not None:
            raise ValueError("Dates must be timezone-naive")
        df["ds"] = df["ds"].dt.normalize()
        df["y"] = pd.to_numeric(df["y"], errors="raise")
        if df.isna().any().any() or not np.isfinite(df["y"]).all():
            raise ValueError("Dates and sales must be complete and finite")

        # group sales datetime data by day
        df = df.groupby("ds").sum().reset_index()

        if len(df) < 2:
            raise ValueError("At least two distinct days are required")

        print("size of aggregated data: ", df.shape)

        print("min date: ", df["ds"].min())
        print("max date: ", df["ds"].max())

        return df
    except Exception as e:
        print(f"Error processing the data file: {e}")
        raise
