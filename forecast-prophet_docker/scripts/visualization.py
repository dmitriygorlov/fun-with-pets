from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


def save_visualizations(model, forecast, output_dir="/results"):
    """Export static PNGs without a browser or Kaleido runtime."""
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    fig = model.plot(forecast, xlabel="Date", ylabel="Sales")
    fig.savefig(output / "forecast.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    fig = model.plot_components(forecast)
    fig.savefig(output / "forecast_components.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
