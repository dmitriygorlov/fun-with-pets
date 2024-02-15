from prophet.plot import plot_plotly, plot_components_plotly


def save_visualizations(model, forecast):
    """
    Generate and save visualizations of the forecast and its components using Plotly, with custom axis labels.
    """

    fig1 = plot_plotly(model, forecast)
    fig1.update_layout(
        xaxis_title="Date",
        yaxis_title="Sales",
        yaxis=dict(range=[0, forecast["yhat"].max()]),
        title="Sales Forecast",
    )
    fig1.write_image("/results/forecast.png")

    fig2 = plot_components_plotly(model, forecast)
    fig2.write_image("/results/forecast_components.png")
