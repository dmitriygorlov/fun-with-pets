import unittest

from scripts.offline import PurchaseRecommender, evaluate, timestamp


class OfflineTests(unittest.TestCase):
    def setUp(self):
        self.before = timestamp("2024-01-01T00:00:00Z")
        self.cutoff = timestamp("2024-02-01T00:00:00Z")
        self.end = timestamp("2024-03-01T00:00:00Z")
        self.train = [("u", "a", self.before), ("v", "b", self.before)]

    def test_empty(self):
        report, model = evaluate([], self.cutoff, self.end)
        self.assertIsNone(report["popularity"]["recall_at_k"])
        self.assertEqual(model.recommend("unknown"), [])

    def test_unknown_singleton_and_candidates(self):
        model = PurchaseRecommender(self.train[:1])
        self.assertEqual(model.recommend("unknown"), ["a"])
        self.assertEqual(model.recommend("u"), [])
        self.assertEqual(model.recommend("unknown", candidates=["missing"]), [])
        self.assertEqual(model.recommend("unknown", k=0), [])

    def test_temporal_boundary_and_unknown_target_denominator(self):
        events = self.train + [("u", "b", self.cutoff),
                               ("u", "new", self.cutoff),
                               ("u", "ignored", self.end)]
        report, model = evaluate(events, self.cutoff, self.end, k=1)
        self.assertEqual(set(model.popularity), {"a", "b"})
        self.assertEqual(report["train_rows"], 2)
        self.assertEqual(report["unknown_target_pairs"], 1)
        self.assertEqual(report["popularity"]["recall_at_k"], 0.5)
        self.assertEqual(report["popularity"]["ndcg_at_k"], 1)

    def test_future_cannot_change_fitted_recommendations(self):
        _, first = evaluate(self.train, self.cutoff, self.end)
        future = [("u", "x", self.cutoff)] * 100
        _, second = evaluate(self.train + future, self.cutoff, self.end)
        for method in ("popularity", "copurchase"):
            self.assertEqual(first.recommend("u", method=method),
                             second.recommend("u", method=method))

    def test_duplicates_repeat_purchases_and_cold_users(self):
        events = self.train * 2 + [("u", "a", self.cutoff),
                                  ("cold", "b", self.cutoff)] * 2
        report, model = evaluate(events, self.cutoff, self.end, k=2)
        self.assertEqual(model.popularity["a"], 1)
        self.assertEqual(report["evaluated_users"], 1)
        self.assertEqual(report["cold_users"], 1)
        self.assertEqual(report["popularity"]["precision_at_k"], 0.5)

    def test_copurchase_personalizes(self):
        model = PurchaseRecommender([
            (user, item, self.before) for user, items in
            [("u", ["a"]), ("v", ["a", "b"]), ("w", ["c"]), ("x", ["c"])]
            for item in items
        ])
        self.assertEqual(model.recommend("u", 1), ["c"])
        self.assertEqual(model.recommend("u", 1, "copurchase"), ["b"])

    def test_validation(self):
        with self.assertRaises(ValueError):
            timestamp("2024-01-01")
        with self.assertRaises(ValueError):
            evaluate([], self.end, self.cutoff)
        with self.assertRaises(ValueError):
            evaluate([], self.cutoff, self.end, k=0)


if __name__ == "__main__":
    unittest.main()
