from prophet import Prophet


def train_model(df, country, seed=42):
    """
    Train the Prophet model with the prepared data and add holidays based on the country specified in the .env file (if available)
    """

    model = Prophet()

    try:
        model.add_country_holidays(country_name=country)
    except KeyError:
        print(f"No holidays found for {country}")

    model.fit(df, seed=seed)
    return model
