from prophet import Prophet


def train_model(df):
    """Train the Prophet model with the prepared data."""
    model = Prophet()
    model.fit(df)
    return model
