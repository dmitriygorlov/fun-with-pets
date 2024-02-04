def make_forecast(model, periods):
    """Use the trained model to make a forecast."""
    future = model.make_future_dataframe(periods=periods)
    forecast = model.predict(future)
    return forecast
