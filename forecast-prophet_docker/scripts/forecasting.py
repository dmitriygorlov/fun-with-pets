from pathlib import Path


def make_forecast(model, periods, output_dir="/results"):
    """
    Generate forecast and save CSV files with both the summary and the full forecast data.
    """

    if isinstance(periods, bool) or not isinstance(periods, int) or periods < 1:
        raise ValueError("Forecast days must be a positive integer")
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)

    # Create future dataframe and make forecast
    future = model.make_future_dataframe(periods=periods)
    forecast = model.predict(future)

    # Save summary forecast with rounded values
    forecast_summary = forecast[["ds", "yhat"]].copy()
    forecast_summary.columns = ["date", "sales"]
    forecast_summary["sales"] = forecast_summary["sales"].round(2)
    forecast_summary.to_csv(output / "forecast_summary.csv", index=False)

    # Save full forecast with components
    forecast.to_csv(output / "forecast_full.csv", index=False)

    return forecast
