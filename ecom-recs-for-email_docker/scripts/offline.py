"""Small deterministic purchase-only benchmark; no service or model downloads."""

import argparse
import csv
import json
import math
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path


def timestamp(value):
    result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if result.tzinfo is None:
        raise ValueError("Timestamps must include a timezone")
    return result.astimezone(timezone.utc)


def load_events(path):
    with open(path, newline="", encoding="utf-8") as source:
        rows = list(csv.DictReader(source))
    events = []
    for row in rows:
        if not row["client_id"].strip() or not row["item_id"].strip():
            raise ValueError("IDs must be nonempty")
        events.append((row["client_id"], row["item_id"], timestamp(row["timestamp"])))
    return events


class PurchaseRecommender:
    """Rank by unique-buyer popularity or item co-purchase, with popularity fallback."""

    def __init__(self, events):
        self.history = defaultdict(set)
        for user, item, _ in events:
            self.history[user].add(item)
        self.popularity = Counter()
        self.pairs = defaultdict(Counter)
        for basket in self.history.values():
            self.popularity.update(basket)
            for item in basket:
                self.pairs[item].update(basket - {item})

    def recommend(self, user, k=3, method="popularity", candidates=None):
        if k < 0 or method not in {"popularity", "copurchase"}:
            raise ValueError("Invalid k or recommendation method")
        seen = self.history.get(user, set())
        allowed = set(self.popularity) if candidates is None else set(candidates)
        allowed &= self.popularity.keys()
        scores = Counter()
        if method == "copurchase":
            for item in sorted(seen):
                for other, count in self.pairs[item].items():
                    scores[other] += count / math.sqrt(
                        self.popularity[item] * self.popularity[other]
                    )
        return sorted(allowed - seen, key=lambda item: (
            -scores[item], -self.popularity[item], item
        ))[:k]


def evaluate(events, cutoff, end, k=3):
    if cutoff >= end or k < 1:
        raise ValueError("Require cutoff < end and k >= 1")
    train = [event for event in events if event[2] < cutoff]
    model = PurchaseRecommender(train)
    targets = defaultdict(set)
    heldout_rows = 0
    for user, item, time in events:
        if cutoff <= time < end:
            heldout_rows += 1
            if item not in model.history.get(user, set()):
                targets[user].add(item)
    report = {
        "train_rows": len(train), "heldout_rows": heldout_rows,
        "evaluated_users": len(targets), "train_catalog": len(model.popularity),
        "cold_users": sum(user not in model.history for user in targets),
        "unknown_target_pairs": sum(
            item not in model.popularity for items in targets.values() for item in items
        ),
        "cutoff": cutoff.isoformat(), "end_exclusive": end.isoformat(), "k": k,
    }
    for method in ("popularity", "copurchase"):
        precision, recall, ndcg, recommended = [], [], [], set()
        for user, relevant in sorted(targets.items()):
            recs = model.recommend(user, k, method)
            hits = sum(item in relevant for item in recs)
            precision.append(hits / k)
            recall.append(hits / len(relevant))
            dcg = sum(1 / math.log2(rank + 2) for rank, item in enumerate(recs)
                      if item in relevant)
            ideal = sum(1 / math.log2(rank + 2) for rank in range(min(k, len(relevant))))
            ndcg.append(dcg / ideal)
            recommended.update(recs)
        report[method] = {
            "precision_at_k": sum(precision) / len(precision) if precision else None,
            "recall_at_k": sum(recall) / len(recall) if recall else None,
            "ndcg_at_k": sum(ndcg) / len(ndcg) if ndcg else None,
            "catalog_coverage": len(recommended) / len(model.popularity)
            if model.popularity and targets else None,
        }
    return report, model


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--events", type=Path, default=Path("examples/events.csv"))
    parser.add_argument("--cutoff", default="2024-02-01T00:00:00Z")
    parser.add_argument("--end", default="2024-03-01T00:00:00Z")
    parser.add_argument("--k", type=int, default=3)
    parser.add_argument("--output", type=Path, default=Path("results/offline.json"))
    args = parser.parse_args()
    report, model = evaluate(load_events(args.events), timestamp(args.cutoff),
                             timestamp(args.end), args.k)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    with args.output.with_suffix(".csv").open("w", newline="", encoding="utf-8") as out:
        writer = csv.writer(out)
        writer.writerow(["client_id", "item_id", "rank"])
        for user in sorted(model.history):
            for rank, item in enumerate(model.recommend(user, args.k, "copurchase"), 1):
                writer.writerow([user, item, rank])
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
