"""DAG for harvesting and converting OAI data Vlaamse Kunst Collectie to target MAM."""
import time
from pprint import pprint

from airflow import DAG
from airflow.operators.python import PythonOperator, PythonVirtualenvOperator
from airflow.utils.dates import days_ago

from task_services.oai_api import OaiApi
from task_services.xml_transformer import XmlTransformer
from task_services.rabbit_publisher import RabbitPublisher

from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook

DB_CONNECT_ID = 'postgres_default'
BATCH_SIZE = 100

args = {
    'owner': 'airflow',
}

dag = DAG(
    dag_id='vkc_oai_harvester',
    default_args=args,
    schedule_interval=None,
    start_date=days_ago(2),
    tags=['VKC'],
)


def reset_table():
    conn = PostgresHook(postgres_conn_id=DB_CONNECT_ID).get_conn()
    cursor = conn.cursor()
    cursor.execute( "TRUNCATE TABLE harvest_oai" )
    conn.commit()
    cursor.close()
    conn.close()


def harvest_oai(**context):
    print("context=",context)

    full_sync = context['full_sync']
    if full_sync:
        print("Full sync requested, clearing harvest table")
        # reset_table() #disable until rabbit publisher is completed
    else:
        print("Delta sync requested, todo: run query to get last_oai_datetime to pass into list_records")

    conn = PostgresHook(postgres_conn_id=DB_CONNECT_ID).get_conn()
    cursor = conn.cursor()
    api = OaiApi()
    records, token, total = api.list_records()
    total_count=len(records)

    while len(records)>0:
        progress = round((total_count/total)*100,1)
        print(f"Saving {len(records)} of {total} records, progress is {progress} %", flush=True)
        for record in records:
            cursor.execute(
                """
                INSERT INTO harvest_oai (data, mam_data, updated_at)
                VALUES(%s, NULL, now())
                """,
                (record,)
            )
        conn.commit()  # commit the insert otherwise its not stored

        if total_count >= total:
            break

        # fetch next batch of records with api
        records, token, total = api.list_records(resumptionToken=token)
        total_count += len(records)

    cursor.close()
    conn.close()

def transform_lido_to_mh(**context):
    print(f'transform_lido_to_mh called with context={context} transform xml format by iterating database')
    tr = XmlTransformer()

    # Notice: using server cursor, makes batches work
    # we open a second connection and cursor to do our update calls for eatch batch
    read_conn = PostgresHook(postgres_conn_id=DB_CONNECT_ID).get_conn()
    update_conn = PostgresHook(postgres_conn_id=DB_CONNECT_ID).get_conn()

    rc = read_conn.cursor('serverCursor')
    rc.execute('select * from harvest_oai')
    while True:
        records = rc.fetchmany(size=BATCH_SIZE)
        if not records:
            break
        print(f"fetched {len(records)} records, now converting...", flush=True)
        uc = update_conn.cursor()
        for record in records:
            record_id = record[0]
            # TODO check: moet de record gesynced worden? (bestaat de record bij meemoo?)

            converted_record = tr.convert(record[1]) 
            uc.execute(
                """
                UPDATE harvest_oai
                SET mam_data = %s,
                    updated_at = now()
                WHERE id=%s
                """,
                (converted_record, record_id)
            )
    
        update_conn.commit()  # commit all updates current batch
        uc.close()

    rc.close()
    read_conn.close()

def publish_to_rabbitmq(**context):
    print(f'publish_to_rabbitmq called with context={context} pushes data to rabbit mq')
    rp = RabbitPublisher()
    rp.publish('some record data')
    time.sleep(3)


with dag:
    # postgres_default is defined in the admin/connections (its just another entry in the airflow database).
    create_db_table = PostgresOperator(
      task_id="create_harvest_table",
      postgres_conn_id=DB_CONNECT_ID,
      sql="sql/harvest_oai_table.sql"
    )

    harvest_oai_task = PythonOperator(
        task_id='harvest_oai',
        python_callable=harvest_oai,
        op_kwargs={'full_sync': True}
    )

    transform_lido_task = PythonOperator(
        task_id='transform_lido_to_mh',
        python_callable=transform_lido_to_mh,
    )

    publish_to_rabbitmq_task = PythonOperator(
        task_id='publish_to_rabbitmq',
        python_callable=publish_to_rabbitmq,
    )

    # for deltas we dont clear our table
    # clear_harvest_table = PostgresOperator(
    #     task_id="clear_harvest_table", 
    #     postgres_conn_id=DB_CONNECT_ID, 
    #     sql="TRUNCATE TABLE harvest_oai;"
    # )

    create_db_table >> harvest_oai_task >> transform_lido_task >> publish_to_rabbitmq_task
    # >> clear_harvest_table


