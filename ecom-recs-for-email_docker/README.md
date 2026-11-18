# E-commerce recommendations: a reproducible offline case

Independent portfolio project for choosing products for a customer email campaign.
The decision is whether personalized ranking merits an online experiment against a
simple popularity baseline. This is not a client deployment or evidence of sales uplift.

## Run the small case

From `ecom-recs-for-email_docker`, with Python 3.13 (standard library only):

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

Validated on Windows / Python 3.13.7 and also Python 3.11.13. The test environment deliberately excludes
LightFM: predictor tests use tiny explicit embeddings and exercise actual CSV I/O
and sklearn neighbor search. Tests cover temporal boundaries, future independence,
metric denominators, duplicates, cold start, empty inputs, and original predictor
regressions. The initial pandas 1.5.2 environment emitted NumPy deprecation warnings; the modern profile removes those warnings.
The original repository had no tests or configured linter. Running the six predictor
regression tests against the original source produced ten errors including subtests.

## Dependency profiles and container verification

The verified profile is Python 3.13.7 (`.python-version` selects 3.13), NumPy
2.4.6, pandas 3.1.1, SciPy 1.17.1, scikit-learn 1.9.1, and Ruff 0.14.5.
`requirements-modern.txt` installs prediction dependencies;
`requirements-test.txt` adds the linter. The offline benchmark needs none of them.
A clean Python 3.13 environment was installed and checked; the same tests also
passed on Python 3.11.13 with the modern scientific libraries.

[pandas 3.1.1](https://pypi.org/project/pandas/3.1.1/) and
[scikit-learn 1.9.1](https://pypi.org/project/scikit-learn/1.9.1/) were checked
against their published packages. Versions are an explicitly tested combination,
not a promise that every dependency is the newest release. Upgrading exposed a
real compatibility issue: NumPy array_split no longer preserved pandas Series;
explicit iloc slices now preserve mapping behavior on both old and modern stacks.

Container follow-up on Upper (2026-11-18): the original Python 3.9 image built,
but failed at startup with pandas 1.5.2 / NumPy 2.0.2 binary incompatibility
(`numpy.dtype size changed`). The Dockerfile now uses Python 3.11 and a
separate training profile: LightFM 1.17, NumPy 1.26.4, pandas 2.3.3, SciPy 1.17.1,
and scikit-learn 1.9.1. The actual tested Python was 3.11.18 on Linux / GCC 14.2.0,
Docker Engine 29.5.3. LightFM requires a legacy build path with pip 24.3.1,
setuptools 68.2.2 and wheel 0.45.1; these are compatibility pins, not newest versions.
The modern prediction-only profile remains separate; do not install both profiles
into the same environment. Native Windows LightFM still needs C++ Build Tools.

The fixed image built successfully. An isolated run of the actual main.py on 12
synthetic training pairs completed four epochs and returned 18 recommendations.
Assertions verified uniqueness, exclusion of prior purchases and unknown IDs.
All 14 original tests passed in that check. Integration review adds three tests for
ID types, metric denominators and empty cohorts; the final 17-test suite, temporal
benchmark CLI and pip check were rerun on the combined code.
This is a functional smoke test, not a LightFM ranking-quality or revenue claim.
pandas 2.3 emits a nonfatal concat FutureWarning in the predictor.

The test used no Compose startup or .env: docker run had --network none,
--read-only, --cap-drop ALL, --security-opt no-new-privileges, read-only synthetic
input/test mounts, and tmpfs for logs, results and embeddings. .dockerignore now
allowlists source files so data and secrets cannot enter the build context.
Compose configuration was inspected but its default host mounts were not used.
Production-scale performance, real data, and Compose startup remain outside this
verification. No service was deployed. Base image/transitive dependency versions are
not fully locked, so future rebuilds still require regression checks.
