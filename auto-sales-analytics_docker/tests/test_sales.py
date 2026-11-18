import tempfile
import unittest
from pathlib import Path

import pandas as pd
from scripts._common import save_to_excel
from scripts.abc_analysis import perform_abc
from scripts.xyz_analysis import perform_xyz


class SalesTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "sales.csv"

    def data(self, rows):
        pd.DataFrame(rows, columns=["product_id", "product_price", "quantity"]).to_csv(
            self.path, index=False
        )

    def test_reconciliation_and_excel(self):
        self.data([(1, 40, 2), (2, 15, 1), (3, 5, 1)])
        result = perform_abc(self.path)
        self.assertEqual(
            result["ABC classification"]["category"].tolist(), ["A", "B", "C"]
        )
        self.assertEqual(result["ABC stats"]["total_sales"].sum(), 100)
        output = Path(self.temp.name) / "nested"
        save_to_excel(result, "ABC", output)
        self.assertEqual(
            len(pd.read_excel(output / "ABC.xlsx", sheet_name="ABC classification")), 3
        )

    def test_xyz_zero_and_population_variation(self):
        self.data([(1, 1, 1), (1, 3, 1), (2, 0, 1), (3, 4, 1)])
        frame = perform_xyz(self.path)["XYZ classification"].set_index("product_id")
        self.assertAlmostEqual(frame.loc[1, "cv"], 0.5)
        self.assertTrue(pd.isna(frame.loc[2, "cv"]))
        self.assertEqual(frame.loc[2, "category"], "Z")
        self.assertEqual(frame.loc[3, "cv"], 0)

    def test_invalid_and_zero(self):
        for rows in [
            [],
            [(1, -1, 1)],
            [(1, float("inf"), 1)],
            [(None, 1, 1)],
            [(1, 0, 1)],
        ]:
            with self.subTest(rows=rows):
                self.data(rows)
                with self.assertRaises(ValueError):
                    perform_abc(self.path)

    def test_large_integer_revenue_does_not_wrap(self):
        self.data([(1, 10**12, 10**12)])
        result = perform_abc(self.path)["ABC classification"]
        self.assertEqual(result["sales"].iloc[0], 1e24)
        self.assertEqual(result["category"].iloc[0], "C")

    def test_large_cv_is_finite(self):
        self.data([(1, 1e200, 1), (1, 3e200, 1)])
        self.assertAlmostEqual(
            perform_xyz(self.path)["XYZ classification"]["cv"].iloc[0], 0.5
        )
