import pickle
import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

from scripts.predict import generate_item_recommendations_for_clients, read_input


class PredictTests(unittest.TestCase):
    def test_zero_byte_input(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "empty.csv"
            path.touch()
            self.assertTrue(read_input(path, ["client_id"]).empty)

    def run_case(self, clients, items, exclusions=(), k=3,
                 user_ids=(1, 2), item_ids=(10, 20)):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            fitted = {
                "clients_mapping": dict(zip(user_ids, range(2))),
                "items_mapping": dict(zip(item_ids, range(2))),
                "items_embeddings": np.array([[1., 0.], [0., 1.]]),
                "client_embeddings": np.array([[1., 0.], [0., 1.]]),
            }
            with (root / "model.pkl").open("wb") as out:
                pickle.dump(fitted, out)
            pd.DataFrame({"client_id": clients}).to_csv(root / "clients.csv", index=False)
            pd.DataFrame({"item_id": items}).to_csv(root / "items.csv", index=False)
            pd.DataFrame(exclusions, columns=["client_id", "item_id"]).to_csv(
                root / "exclude.csv", index=False)
            generate_item_recommendations_for_clients(
                root / "model.pkl", root / "clients.csv", root / "items.csv",
                root / "exclude.csv", root / "result.csv", k, 1, 10)
            return pd.read_csv(root / "result.csv")

    def test_singleton(self):
        self.assertEqual(self.run_case([1], [10]).values.tolist(), [[1, 10, 1]])

    def test_string_and_large_integer_ids(self):
        for users, items in [(('user-a', 'user-b'), ('item-a', 'item-b')),
                             ((2**40, 2**40 + 1), (2**41, 2**41 + 1))]:
            with self.subTest(users=users):
                result = self.run_case([users[0]], [items[0]],
                                       user_ids=users, item_ids=items)
                self.assertEqual(result.values.tolist(), [[users[0], items[0], 1]])

    def test_unknowns_are_removed(self):
        self.assertEqual(self.run_case([1, 999], [10, 999]).values.tolist(), [[1, 10, 1]])

    def test_empty_unknown_and_zero(self):
        for clients, items in [([], [10]), ([1], []), ([999], [10]), ([1], [999])]:
            with self.subTest(clients=clients, items=items):
                result = self.run_case(clients, items)
                self.assertTrue(result.empty)
                self.assertEqual(list(result), ["client_id", "item_id", "rank"])
        self.assertTrue(self.run_case([1], [10], k=0).empty)

    def test_deduplicates_excludes_and_reranks(self):
        self.assertEqual(self.run_case([1, 1], [10, 20, 20], [(1, 10)]).values.tolist(),
                         [[1, 20, 1]])

    def test_all_excluded(self):
        self.assertTrue(self.run_case([1], [10], [(1, 10)]).empty)

    def test_exact_chunk_boundaries(self):
        self.assertEqual(len(self.run_case([1, 2], [10, 20])), 4)


if __name__ == "__main__":
    unittest.main()
