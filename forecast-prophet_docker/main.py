from scripts.data_preparation import prepare_data
from scripts.model_training import train_model
from scripts.forecasting import make_forecast
from scripts.visualization import save_visualization


def main():
    df = prepare_data("/data/example.csv")

    model = train_model(df)

    forecast = make_forecast(model, periods=365)  # forecast for the next 365 days

    forecast.to_csv("/results/forecast.csv", index=False)

    save_visualization(forecast, "/results/forecast.png")


if __name__ == "__main__":
    main()
