# E-commerce recommendations: a reproducible offline case

Independent portfolio project for choosing products for a customer email campaign.
The decision is whether personalized ranking merits an online experiment against a
simple popularity baseline. This is not a client deployment or evidence of sales uplift.

## Run the small case

From `ecom-recs-for-email_docker`, with Python 3.11 (standard library only):

```sh
python -m scripts.offline
```

This reads `examples/events.csv` and writes `results/offline.json` and
`results/offline.csv` (client_id, item_id, rank). The 20 rows are explicitly
hand-authored synthetic purchases, not customer data. No credentials, downloads,
paid calls, or emails are involved. To use another timestamped CSV:

```sh
python -m scripts.offline --events examples/events.csv --cutoff 2024-02-01T00:00:00Z --end 2024-03-01T00:00:00Z --k 3
```

IDs are nonempty strings. Timestamps require timezones. Empty training data returns
no recommendations; empty evaluation cohorts produce null metrics rather than a
fabricated zero. Unknown customers get popularity fallback; unknown candidate items
are excluded. Already purchased items are excluded; ties resolve by item ID.
The exported recommendations cover training customers; the API also accepts cold users.

## Ranking and evaluation contract

Popularity counts distinct buyers per item, so duplicate events do not inflate it.
The personalized comparator sums cosine-normalized co-purchase counts over the
customer's past items, then breaks ties with popularity and item ID. It is a small,
inspectable item-item baseline, not an evaluation of the existing LightFM model.
Its quadratic work within each customer's history limits it to compact examples.

One global cutoff defines training (`timestamp < cutoff`) and test
(`cutoff <= timestamp < end`). All histories, counts, item candidates, and
co-purchase pairs come exclusively from training. There is no random split, future
catalog discovery, test-driven tuning, or sampled-negative evaluation.

Targets are distinct new-to-user items in the test window. Repeated purchases of
training items are outside this acquisition objective. Users with no such targets
are excluded. Cold users are included; future-only products remain in the target
denominator and cannot be recommended. Reported cold-user and unknown-target
counts make these cases visible. Recommendations are frozen at the cutoff, with
no updates from test purchases.

Metrics are macro-averaged across eligible users: Precision@K = hits / K (including
short lists), Recall@K = hits / distinct targets, NDCG@K uses binary relevance and
log2 rank discount. Catalog coverage = distinct recommended items / training
catalog. These measure retrieval, ranking, and breadth, not causal business value.

Measured default synthetic run: 12 training rows, 8 held-out rows, 6 eligible users,
5 training items, 1 cold user, 1 unknown target pair. K=3:

| Model | Precision@3 | Recall@3 | NDCG@3 | Catalog coverage |
|---|---:|---:|---:|---:|
| Popularity | 0.277778 | 0.750000 | 0.479168 | 1.000000 |
| Co-purchase | 0.333333 | 0.916667 | 0.790679 | 1.000000 |

These tiny, designed data validate execution only; the difference is not a reliable
model-selection result. Real logs have exposure bias, returns, availability changes,
and purchases without recommendation exposure. The example assumes training items
remain available; a real evaluation needs a catalog snapshot at the cutoff.
Use separate earlier temporal validation windows for tuning and an untouched later
test window; report uncertainty and warm/cold segments on a sufficiently large dataset.

## Business experiment before rollout

Randomize consented eligible customers persistently between popularity and the
chosen ranking, keeping send time, design, discounts, and available inventory equal.
Predefine the attribution window, primary metric (net revenue per randomized
customer after returns), minimum worthwhile effect, power/sample size, and duration
before launch. Track conversion and clicks as secondary diagnostics; unsubscribe,
complaints, delivery failures, and margin are guardrails. Analyze intention-to-treat
with uncertainty; avoid repeated significance peeking. Log exposures and item stock.
An offline improvement alone does not establish incremental revenue.

## Existing LightFM pipeline and regression fix

The original `main.py` trains LightFM from `files/client_item.csv` and predicts for
`clients.csv` and `items.csv`, excluding pairs from `exclude.csv`. CSVs use the first
one or two columns; IDs must have consistent types across files. The predictor
skips unknown users/items (unlike the new benchmark's popularity fallback).
Empty or header-only prediction inputs, single IDs, duplicates, and all-excluded
requests now produce valid CSVs. `k=0` produces headers only. `chunk` and
`n_neighbors` must be positive. The existing neighbor limit can return fewer than
K results after exclusions; increase K_SPARE for this legacy pipeline.

Confirmed on pandas 1.5.2: DataFrame masking retained unknown IDs as NaN, causing
invalid embedding indices, and squeeze converted one-row input to a scalar. Row
filtering now keeps Series shape. Chunk counting no longer creates empty batches
when the customer count is exactly divisible by the chunk size. IDs are no longer
forced into int32. Logging creates its own directory on local runs.

Legacy Docker command remains `docker compose up --build`; its configured mounts
and environment variables are in `docker-compose.yml`. Only load trusted model
pickle files. The original large `files/` samples are not used by the new example.

## Checks and limits

```sh
python -m venv .venv
# Activate .venv (Windows: .venv\Scripts\activate)
python -m pip install -r requirements-test.txt
python -m unittest discover -s tests -v
python -m ruff check scripts tests
python -m scripts.offline
```

Validated on Windows / Python 3.11.13. The test environment deliberately excludes
LightFM: predictor tests use tiny explicit embeddings and exercise actual CSV I/O
and sklearn neighbor search. Tests cover temporal boundaries, future independence,
metric denominators, duplicates, cold start, empty inputs, and original predictor
regressions. pandas emits NumPy deprecation warnings; they are not test failures.
The original repository had no tests or configured linter. Running the six predictor
regression tests against the original source produced ten errors including subtests.

Full LightFM training and Docker integration were NOT validated: LightFM 1.16 and
1.17 failed package metadata/build setup in this Windows environment
(`__LIGHTFM_SETUP__`), and the Docker engine was unavailable. The original training
code/dependencies remain unchanged; no LightFM performance claim is made. The
benchmark and predictor regression tests can run independently of that limitation.
