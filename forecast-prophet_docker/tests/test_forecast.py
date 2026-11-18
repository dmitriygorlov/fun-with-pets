import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd
from scripts.data_preparation import prepare_data
from scripts.forecasting import make_forecast
from scripts.model_training import train_model
from scripts.visualization import save_visualizations


class ForecastTests(unittest.TestCase):
    def test_synthetic_pipeline(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            source = root / "input.csv"
            pd.DataFrame(
                {
                    "date": pd.date_range("2024-01-01", periods=90),
                    "sales": 20 + np.arange(90) * 0.1 + np.sin(np.arange(90)),
                }
            ).to_csv(source, index=False)
            data = prepare_data(source)
            model = train_model(data, "US")
            forecast = make_forecast(model, 7, root)
            self.assertEqual(len(forecast), 97)
            self.assertTrue(np.isfinite(forecast["yhat"]).all())
            save_visualizations(model, forecast, root)
            for name in ["forecast.png", "forecast_components.png"]:
                self.assertEqual((root / name).read_bytes()[:8], b"\x89PNG\r\n\x1a\n")
            self.assertEqual(len(pd.read_csv(root / "forecast_summary.csv")), 97)
            second = make_forecast(train_model(data, "US"), 7, root)
            np.testing.assert_allclose(forecast["yhat"], second["yhat"], atol=1e-8)

    def test_validation_and_daily_aggregation(self):
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder) / "input.csv"
            source.write_text("date,sales\n2024-01-01,2\n2024-01-01,3\n2024-01-02,4\n")
            self.assertEqual(prepare_data(source)["y"].tolist(), [5, 4])
            for value in ["nan", "inf", "bad"]:
                source.write_text(f"date,sales\n2024-01-01,{value}\n2024-01-02,1\n")
                with self.assertRaises(ValueError):
                    prepare_data(source)
        for value in [0, -1, 1.5, True]:
            with self.assertRaises(ValueError):
                make_forecast(None, value)
