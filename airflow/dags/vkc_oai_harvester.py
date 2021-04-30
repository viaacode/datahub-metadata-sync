"""DAG for harvesting and converting OAI data Vlaamse Kunst Collectie to target MAM."""
import time
from pprint import pprint

from airflow import DAG
from airflow.operators.python import PythonOperator, PythonVirtualenvOperator
from airflow.utils.dates import days_ago

from task_services.vkc_api import VkcApi
from task_services.xml_transformer import XmlTransformer
from task_services.rabbit_publisher import RabbitPublisher
from task_services.mediahaven_api import MediahavenApi
from task_services.harvest_table import HarvestTable

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


def harvest_vkc(**context):
    print("context=",context)

    full_sync = context['full_sync']
    if full_sync:
        print("Full sync requested")
        HarvestTable.truncate( PostgresHook(postgres_conn_id=DB_CONNECT_ID).get_conn() )
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
            HarvestTable.insert(cursor, record)    

        conn.commit()  # commit batch of inserts

        if total_count >= total:
            break  # exit loop, we have all records from vkc

        # fetch next batch of records with api
        records, token, total = api.list_records(resumptionToken=token)
        total_count += len(records)

    cursor.close()
    conn.close()

def transform_lido_to_mh(**context):
    print(f'transform_lido_to_mh called with context={context} transform xml format by iterating database')
    tr = XmlTransformer()
    mh_api = MediahavenApi()

    # Notice: using server cursor, makes batches work
    # we open a second connection and cursor to do our update calls for eatch batch
    read_conn = PostgresHook(postgres_conn_id=DB_CONNECT_ID).get_conn()
    update_conn = PostgresHook(postgres_conn_id=DB_CONNECT_ID).get_conn()

    rc = read_conn.cursor('serverCursor')
    HarvestTable.batch_select_records(rc)
    while True:
        records = rc.fetchmany(size=BATCH_SIZE)
        if not records:
            break
        print(f"fetched {len(records)} records, now converting...", flush=True)
        uc = update_conn.cursor()
        for record in records:
            if mh_api.vkc_record_exists(HarvestTable.get_work_id(record)):
                print(f"Skipping existing entry, work_id = {HarvestTable.get_work_id(record)}")
                HarvestTable.set_synchronized(uc, record, True) 
            else:
                converted_record = tr.convert(record[1]) 
                HarvestTable.update_mam_xml(uc, record, converted_record)
 
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
    HarvestTable.batch_select_records(rc)
    while True:
        records = rc.fetchmany(size=BATCH_SIZE)
        if not records:
            break
        print(f"fetched {len(records)} records, pushing on rabbitmq...", flush=True)
        uc = update_conn.cursor()
        for record in records:
            rp.publish(record)
            HarvestTable.set_synchronized(uc, record, True) 
    
        update_conn.commit()  # commit all updates current batch
        uc.close()

    rc.close()
    read_conn.close()



with dag:
    # postgres_default is defined in the admin/connections (its just another entry in the airflow database).
    create_db_table = PostgresOperator(
      task_id="create_harvest_table",
      postgres_conn_id=DB_CONNECT_ID,
      sql=HarvestTable.create_sql()
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


