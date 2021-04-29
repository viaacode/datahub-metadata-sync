"""DAG for harvesting and converting OAI data Vlaamse Kunst Collectie to target MAM."""
import time
from pprint import pprint

from airflow import DAG
from airflow.operators.python import PythonOperator, PythonVirtualenvOperator
from airflow.utils.dates import days_ago

from task_services.vkc_api import VkcApi
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
    print("Clearing harvest_vkc table")
    conn = PostgresHook(postgres_conn_id=DB_CONNECT_ID).get_conn()
    cursor = conn.cursor()
    cursor.execute( "TRUNCATE TABLE harvest_vkc" )
    conn.commit()
    cursor.close()
    conn.close()


def harvest_vkc(**context):
    print("context=",context)

    full_sync = context['full_sync']
    if full_sync:
        print("Full sync requested")
        reset_table()
    else:
        print("Delta sync requested, todo: run query to get datestamp to pass into list_records")

    conn = PostgresHook(postgres_conn_id=DB_CONNECT_ID).get_conn()
    cursor = conn.cursor()
    api = VkcApi()
    records, token, total = api.list_records()
    total_count=len(records)

    while len(records)>0:
        progress = round((total_count/total)*100,1)
        print(f"Saving {len(records)} of {total} records, progress is {progress} %", flush=True)
        for record in records:
            cursor.execute(
                """
                INSERT INTO harvest_vkc (identifier, published_id, vkc_xml, mam_xml, datestamp)
                VALUES(%s, %s, %s, NULL, %s)
                """,
                (record['identifier'], record['published_id'], record['xml'], record['datestamp'])
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
    rc.execute('select * from harvest_vkc where synchronized=false')
    while True:
        records = rc.fetchmany(size=BATCH_SIZE)
        if not records:
            break
        print(f"fetched {len(records)} records, now converting...", flush=True)
        uc = update_conn.cursor()
        for record in records:
            record_id = record[0]
            # TODO check: moet de record gesynced worden? (bestaat de record bij meemoo?)
            # gebruiken we hier identifier of published_id (tweede is niet altijd aanwezig)
            # mam call nodig hier enzo. Alsook by full_sync toch update doen hier indien al aanwezig???

            to_be_synced = True
            synchronized = not to_be_synced

            converted_record = tr.convert(record[1]) 
            uc.execute(
                """
                UPDATE harvest_vkc
                SET mam_xml = %s,
                    synchronized = %s,
                    updated_at = now()
                WHERE id=%s
                """,
                (converted_record, synchronized, record_id)
            )
    
        update_conn.commit()  # commit all updates current batch
        uc.close()

    rc.close()
    read_conn.close()

def publish_to_rabbitmq(**context):
    print(f'publish_to_rabbitmq called with context={context} pushes data to rabbit mq')
    rp = RabbitPublisher()

    read_conn = PostgresHook(postgres_conn_id=DB_CONNECT_ID).get_conn()
    update_conn = PostgresHook(postgres_conn_id=DB_CONNECT_ID).get_conn()

    rc = read_conn.cursor('serverCursor')
    rc.execute('select * from harvest_vkc where synchronized=false')
    while True:
        records = rc.fetchmany(size=BATCH_SIZE)
        if not records:
            break
        print(f"fetched {len(records)} records, pushing on rabbitmq...", flush=True)
        uc = update_conn.cursor()
        for record in records:
            record_id = record[0]
            rp.publish(record)

            # set synchronized flag to true
            uc.execute(
                """
                UPDATE harvest_vkc
                SET synchronized = 'true',
                    updated_at = now()
                WHERE id=%s
                """,
                (record_id,)
            )
    
        update_conn.commit()  # commit all updates current batch
        uc.close()

    rc.close()
    read_conn.close()



with dag:
    # postgres_default is defined in the admin/connections (its just another entry in the airflow database).
    create_db_table = PostgresOperator(
      task_id="create_harvest_table",
      postgres_conn_id=DB_CONNECT_ID,
      sql="sql/harvest_vkc_table.sql"
    )

    harvest_vkc_task = PythonOperator(
        task_id='harvest_vkc',
        python_callable=harvest_vkc,
        op_kwargs={'full_sync': True}
    )

    transform_lido_task = PythonOperator(
        task_id='transform_xml',
        python_callable=transform_lido_to_mh,
    )

    publish_to_rabbitmq_task = PythonOperator(
        task_id='publish_to_rabbitmq',
        python_callable=publish_to_rabbitmq,
    )

    create_db_table >> harvest_vkc_task >> transform_lido_task >> publish_to_rabbitmq_task


