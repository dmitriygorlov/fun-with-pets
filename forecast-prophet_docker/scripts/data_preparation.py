import pandas as pd


def prepare_data(file_path):
    """Read and preprocess data from CSV file."""
    try:
        df = pd.read_csv(file_path)
        df["ds"] = pd.to_datetime(df["ds"], format="%Y-%m-%d")
        return df
    except Exception as e:
        print(f"Error processing the data file: {e}")
        raise
