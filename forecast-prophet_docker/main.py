import os

from dotenv import load_dotenv
from scripts.data_preparation import prepare_data
from scripts.forecasting import make_forecast
from scripts.model_training import train_model
from scripts.visualization import save_visualizations


def main():
    """Main function to run the complete pipeline."""
    load_dotenv()
    try:
        country = os.getenv("COUNTRY", "US")
        periods = int(os.getenv("FORECAST_DAYS", 365))
        filepath = os.getenv("FILEPATH", "/data/example.csv")
    except Exception as e:
        print(f"Error loading environment variables: {e}")
        raise

    # let's take csv file from /data folder and prepare it for further processing
    df = prepare_data(filepath)

    print(
        "Data prepared successfully, country:",
        country,
        "forecasting for",
        periods,
        "days",
    )

    model = train_model(df, country)

    forecast = make_forecast(model, periods)

    save_visualizations(model, forecast)


if __name__ == "__main__":
    main()
