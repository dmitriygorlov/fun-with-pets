import plotly.graph_objs as go
import pandas as pd


def save_visualization(forecast, file_path):
    """Generate and save a visualization of the forecast using Plotly."""
    trace1 = go.Scatter(
        x=forecast["ds"], y=forecast["yhat"], mode="lines", name="Прогноз"
    )

    trace2 = go.Scatter(
        x=forecast["ds"],
        y=forecast["yhat_upper"],
        fill=None,
        mode="lines",
        line=dict(color="gray"),
        showlegend=False,
    )

    trace3 = go.Scatter(
        x=forecast["ds"],
        y=forecast["yhat_lower"],
        fill="tonexty",
        mode="lines",
        line=dict(color="gray"),
        showlegend=False,
    )

    data = [trace1, trace2, trace3]

    layout = go.Layout(
        title="Прогноз продаж", xaxis=dict(title="Дата"), yaxis=dict(title="Продажи")
    )

    fig = go.Figure(data=data, layout=layout)
    fig.write_image(file_path)  # save the plot to a file
