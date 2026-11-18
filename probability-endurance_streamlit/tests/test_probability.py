import math
import unittest
from pathlib import Path

from probability import cumulative, fraction, trials_for_95
from streamlit.testing.v1 import AppTest


class ProbabilityTests(unittest.TestCase):
    def test_boundaries(self):
        self.assertEqual(cumulative(0, 100), 0)
        self.assertEqual(cumulative(1, 100), 1)
        self.assertEqual(cumulative(1, 0), 0)
        self.assertEqual(trials_for_95(0), math.inf)
        self.assertEqual(trials_for_95(1), 1)
        self.assertAlmostEqual(cumulative(0.5, 2), 0.75)
        self.assertGreater(cumulative(1e-20, 100), 0)
        self.assertEqual(trials_for_95(0.5), 5)

    def test_bad_fractions(self):
        for n, d in [(2, 1), (-1, 3), (1, 0)]:
            with self.assertRaises(ValueError):
                fraction(n, d)

    def test_ui_inputs(self):
        app = AppTest.from_file(
            str(Path(__file__).resolve().parents[1] / "main.py")
        ).run()
        for p in [0.0, 1.0]:
            app.slider[0].set_value(p).run()
            self.assertFalse(app.exception)
        app.radio[0].set_value("Fractional Entry").run()
        app.number_input[0].set_value(8).run()
        self.assertTrue(app.error)
        self.assertFalse(app.exception)
        app.radio[0].set_value("Manual Entry").run()
        app.number_input[1].set_value(1000000).run()
        self.assertFalse(app.exception)
