import requests
from airflow.hooks.postgres_hook import PostgresHook


def fetch_and_store_joke():
    # Fetch joke from API
    response = requests.get("https://official-joke-api.appspot.com/random_joke")
    data = response.json()

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
    return joke[0] + " - " + joke[1]


# If you want to test this script alone
if __name__ == "__main__":
    fetch_and_store_joke()
    fetch_joke_from_db()
