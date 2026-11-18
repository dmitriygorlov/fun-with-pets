from html import escape

import requests
from airflow.providers.postgres.hooks.postgres import PostgresHook


def fetch_and_store_joke():
    # Fetch joke from API
    response = requests.get(
        "https://official-joke-api.appspot.com/random_joke", timeout=15
    )
    response.raise_for_status()
    data = response.json()
    if not all(
        isinstance(data.get(key), str) and data[key] for key in ("setup", "punchline")
    ):
        raise ValueError("Joke API returned invalid content")

    # Get Postgres connection
    pg_hook = PostgresHook(postgres_conn_id="jokes_conn")

    # Check if table 'jokes' exists, if not create it
    table_check_sql = """
        SELECT EXISTS (
        SELECT FROM information_schema.tables 
        WHERE  table_schema = 'public' 
        AND    table_name   = 'jokes'
        );
    """
    table_exists = pg_hook.get_first(table_check_sql)[0]
    if not table_exists:
        create_table_sql = """
            CREATE TABLE jokes (
                id SERIAL PRIMARY KEY,
                setup TEXT NOT NULL,
                punchline TEXT NOT NULL
            );
        """
        pg_hook.run(create_table_sql)

    sql = """INSERT INTO jokes (setup, punchline) VALUES (%s, %s)"""
    pg_hook.run(sql, parameters=(data["setup"], data["punchline"]))


def fetch_joke_from_db():
    pg_hook = PostgresHook(postgres_conn_id="jokes_conn")
    select_sql = """SELECT setup, punchline FROM jokes ORDER BY id DESC LIMIT 1"""
    joke = pg_hook.get_first(select_sql)
    if not joke:
        raise ValueError("No joke found")
    return escape(joke[0]) + " - " + escape(joke[1])
