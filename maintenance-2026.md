# Compatibility maintenance — 2026-11-18

Baseline: 22551a3912f8639070c11a03a3f8585c14e22aae. Independent checkout on Upper; no repository AGENTS.md or .agents skills were present. Existing user branches analytics-tool and gpt_tg_bot are outside this change. ecom-recs-for-email_docker is unchanged, including its pinned dependencies and tests.

## Inventory and dependency decisions

Previous requirements were unpinned (except Plotly >=5), so the historical installed package versions cannot be inferred from the repository.

| Project | Previous runtime/dependencies | New tested target | Preserved purpose / risk |
| --- | --- | --- | --- |
| Sales analytics | Python 3.10; pandas, NumPy, SciPy, openpyxl unpinned | Python 3.14; pandas 3.1.1, NumPy 2.5.5, openpyxl 3.1.5; SciPy removed | ABC/XYZ Excel; validates malformed/zero input, preserves existing ABC boundary convention and transaction-level XYZ |
| Forecast | Python 3.10; Prophet/pandas/dotenv/Kaleido unpinned, Plotly >=5 | Python 3.14; Prophet 1.5.0, pandas 3.1.1, NumPy 2.5.5, dotenv 1.2.4, Matplotlib 3.11.2 | Forecast CSVs and two PNGs; no browser dependency; no quality/backtest claim |
| Probability | Python 3.10; Streamlit/Plotly unpinned | Python 3.14; Streamlit 1.67.0, Plotly 7.1.0 | Same probability calculation, valid boundaries and bounded chart size |
| Translation | Python 3.9; aiogram/translators unpinned, v2 API | Python 3.14; aiogram 3.32.0, deep-translator 1.11.4 | Russian/Turkish round trip; external translation still unofficial |
| GPT helper | Python 3.10; aiogram/OpenAI/pandas/dotenv unpinned, legacy APIs | Python 3.14; aiogram 3.32.0, OpenAI 3.55.0, dotenv 1.2.4; pandas replaced by csv | Async request, auth/history/usage, no prompt/password logging; local sensitive history remains |
| Airflow jokes | Airflow 2.7.2, PostgreSQL 13, Redis latest/Celery | Airflow 3.4.0/Python 3.13; PostgreSQL 18; standard 1.21.0, postgres 7.1.2, smtp 3.2.1, requests 2.34.2 | Local standalone learning stack; new volumes; email opt-in; no automatic old DB migration |

Package versions were checked against official PyPI metadata on the maintenance date. Runtime base tags and transitive dependencies are not fully locked; rebuilds must rerun checks. Airflow uses its supported Python 3.13 image rather than forcing every project onto one interpreter.

## Reproduction

Build each project independently with `docker build -t project-check PROJECT`. Run its tests without credentials/network:

```sh
docker run --rm --network none --entrypoint python -v "$PWD/PROJECT:/work:ro" -w /work project-check -m unittest discover -s tests -v
docker run --rm --network none --entrypoint python project-check -m pip check
```

`maintenance-ruff.toml` applies only when explicitly selected, preserving ecom's lint configuration. The Offline project checks workflow runs all six container suites and ecom's existing checks with read-only repository permissions. Test fixtures are synthetic; bot/API/DB calls are mocked. No real Telegram messages, paid model calls, database operations or emails are test prerequisites.

## Limits and rollback

No measured performance improvement, business impact or forecast accuracy is claimed. Prophet is trained twice on a synthetic daily series to check fixed-seed repeatability, not rolling backtest quality. Existing serialized Prophet models were not supplied or migrated. CSV outputs retain their column names. GPT CSV/JSON state is preserved by schema; back up these files before upgrading. Individual file replacements are atomic but cross-file crash recovery is not transactional.

The repository had no deployment records and only GitHub's dynamic dependency-graph workflow at inspection. No service was deployed by this maintenance. Roll back code by reverting the maintenance commit; for Airflow use the old Compose file and preserved original volumes, never attach an old database directory to a new major PostgreSQL image. No old volume is deleted. See each project README for behavior and migration details.

## Official references

- [Python images](https://hub.docker.com/_/python)
- [pandas releases](https://pandas.pydata.org/docs/whatsnew/index.html)
- [Prophet](https://pypi.org/project/prophet/1.5.0/)
- [aiogram migration](https://docs.aiogram.dev/en/latest/migration_2_to_3.html)
- [OpenAI Python SDK](https://github.com/openai/openai-python)
- [Airflow Docker guide](https://airflow.apache.org/docs/apache-airflow/3.4.0/howto/docker-compose/index.html)

## Local verification results

All six Docker images built successfully. All six environments passed `python -m pip check`.

- Sales: 5 tests, including ABC reconciliation/Excel read-back, invalid input, zero-mean XYZ, integer overflow and large-value CV. The actual container entry point wrote both workbooks from a synthetic three-product CSV.
- Forecast: 2 tests, including daily aggregation, invalid input/horizon, real Prophet fitting, repeated fixed-seed predictions, CSV schema and PNG signatures. The actual container entry point produced both CSVs and PNGs from a synthetic 60-day series. No historical dataset or backtest was available.
- Probability: 3 tests, including Streamlit AppTest for 0/1, invalid fraction and one million trials. A temporary network-isolated server returned `ok` from `/_stcore/health`.
- Translation: 2 mocked async handler tests; no external translation or Telegram call.
- GPT: 2 tests covering authentication, async response, usage persistence, failed request rollback, non-text input, log redaction, and loading legacy CSV/JSON schema including a large user ID. No paid API or Telegram call.
- Airflow: 4 tests for mocked fetch/SQL/HTML and email-disabled/enabled DAG topology. A network-isolated standalone container reported healthy metadata DB, scheduler, triggerer and DAG processor. Its disposable metadata DB was inspected for DAG pause/import status; no production database or SMTP service was used. The PostgreSQL 18 Compose service and old database migration were not exercised.
- Preserved ecom: all 17 existing tests, Ruff 0.14.5, benchmark CLI and dependency compatibility check passed in a separate Python 3.14.10 environment with its unchanged requirements-test.txt. Its legacy LightFM Docker pipeline was not rebuilt in this maintenance; prior verification remains documented in its README.
- Ruff 0.17.5 check/format and `git diff --check` passed for the changed projects. Sales and Airflow Compose config validation passed. Forecast Compose still requires the documented local `.env` file.

Temporary test containers used `--rm`; the named UI/Airflow smoke containers were stopped explicitly. No pre-existing containers, images, volumes, branches or working copies were modified. Task image tags may remain as build cache. Existing user branch tips were checked before integration.
