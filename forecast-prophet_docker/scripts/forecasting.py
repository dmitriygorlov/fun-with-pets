def make_forecast(model, periods):
    """
    Generate forecast and save CSV files with both the summary and the full forecast data.
    """

    # Create future dataframe and make forecast
    future = model.make_future_dataframe(periods=periods)
    forecast = model.predict(future)

    # Save summary forecast with rounded values
    forecast_summary = forecast[["ds", "yhat"]]
    forecast_summary.columns = ["date", "sales"]
    forecast_summary["sales"] = forecast_summary["sales"].round(2)
    forecast_summary.to_csv("/results/forecast_summary.csv", index=False)

    # Save full forecast with components
    forecast.to_csv("/results/forecast_full.csv", index=False)

    return forecast
