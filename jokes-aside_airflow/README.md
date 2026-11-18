# Airflow jokes pipeline

Learning pipeline: public joke API → PostgreSQL → optional email. Airflow 2.7.2 is replaced by 3.4.0/Python 3.13, with current standard, PostgreSQL and SMTP providers. The former Celery/Redis cluster is replaced by the official standalone development mode, appropriate for this one-DAG example. This is not a production deployment.

## Local start

Copy `.env.example` to `.env`, then run `docker compose up --build` in this directory. The UI is bound to localhost:8080. Standalone prints its generated login details locally. The DAG is initially paused. Unpausing it permits public API and database access. Email is absent from the DAG unless `ENABLE_EMAIL=true` and `EMAIL_FOR_REPORT` are explicitly configured; set an SMTP connection with `AIRFLOW_CONN_SMTP_DEFAULT` before enabling delivery. Do not run the DAG as an offline test.

## Migration and rollback

The new Compose uses separate `airflow3-local` and `jokes-postgres18` volumes (PostgreSQL 18). It does not attach to or migrate old Airflow 2/PostgreSQL 13 volumes. Preserve those volumes and back them up. For a real installation, rehearse the official Airflow and PostgreSQL migrations separately; this task does not claim metadata/history migration. The joke table columns remain compatible for an explicit SQL export/import. Roll back code to the prior commit and use the prior Compose configuration with the original volumes; never mount a PostgreSQL 13 data directory into PostgreSQL 18.

## Offline checks

```sh
docker build -t pets-jokes .
docker run --rm --network none --entrypoint python -v "$PWD:/work:ro" -w /work pets-jokes -m unittest discover -s tests -v
docker run --rm --network none --entrypoint python pets-jokes -m pip check
```

Tests mock HTTP/PostgreSQL, check response validation, timeout, parameterized inserts, HTML escaping, and DAG topology. They never execute an EmailOperator or connect to a database. Fetch retries may insert duplicates; API contents are not deduplicated and delivery is not exactly-once. See [maintenance record](../maintenance-2026.md) for exact verification boundaries.
