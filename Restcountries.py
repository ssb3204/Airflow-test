from airflow import DAG
from airflow.decorators import task
from airflow.providers.postgres.hooks.postgres import PostgresHook
from datetime import datetime, timedelta
import requests
import json
import logging


def get_Redshift_cursor():
    hook = PostgresHook(postgres_conn_id='redshift_dev_db')
    return hook.get_conn().cursor()


@task
def fetch_country_data():
    url = "https://restcountries.com/v3/all"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()


@task
def load_to_redshift(data):
    schema = "ryanp3"
    table = "country_info"

    rows = []
    for country in data:
        try:
            name = country["name"]["official"].replace("'", "''")
            population = country.get("population", 0)
            area = country.get("area", 0.0)
            rows.append(f"('{name}', {population}, {area})")
        except KeyError:
            continue

    if not rows:
        raise ValueError("No valid data to insert.")

    cur = get_Redshift_cursor()

    create_table_sql = f"""
        CREATE TABLE IF NOT EXISTS {schema}.{table} (
            name VARCHAR(256),
            population BIGINT,
            area FLOAT
        );
    """

    delete_sql = f"DELETE FROM {schema}.{table};"
    insert_sql = f"INSERT INTO {schema}.{table} (name, population, area) VALUES " + ",".join(rows)

    try:
        logging.info("Creating table if not exists...")
        cur.execute(create_table_sql)
        logging.info("Clearing existing data...")
        cur.execute(delete_sql)
        logging.info("Inserting new data...")
        cur.execute(insert_sql)
        cur.execute("COMMIT;")
    except Exception as e:
        cur.execute("ROLLBACK;")
        logging.error(f"Redshift insertion failed: {e}")
        raise


with DAG(
    dag_id='country_info_to_redshift',
    start_date=datetime(2024, 1, 1),
    schedule='30 6 * * 6',  # 매주 토요일 06:30 UTC
    catchup=False,
    max_active_runs=1,
    default_args={
        'retries': 1,
        'retry_delay': timedelta(minutes=3),
    },
    tags=['country', 'api', 'redshift'],
) as dag:
    raw_data = fetch_country_data()
    load_to_redshift(raw_data)
