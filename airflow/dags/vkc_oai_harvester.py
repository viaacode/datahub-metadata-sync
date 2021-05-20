#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  @Author: Walter Schreppers
#
#   airflow/dags/vkc_oai_harvester.py
#
#   DAG with tasks for harvesting and converting OAI data from
#   Vlaamse Kunst Collectie to target MAM and publish via RabbitMQ
#

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago

from task_services.vkc_api import VkcApi
from task_services.rabbit_publisher import RabbitPublisher
from task_services.mediahaven_api import MediahavenApi
from task_services.harvest_table import HarvestTable
from task_services.mapping_table import MappingTable

# instead of using our xmltransformer directly we use the
# transformer_process wrapper to workaround a memleak in saxonc
# from task_services.xml_transformer import XmlTransformer
from task_services.transformer_process import xml_convert

from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from psycopg2.extras import DictCursor

DB_CONNECT_ID = 'postgres_default'
BATCH_SIZE = 200

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


def synchronize_vkc():
    conn = PostgresHook(postgres_conn_id=DB_CONNECT_ID).get_conn()
    cursor = conn.cursor(cursor_factory=DictCursor)
    last_synced = HarvestTable.get_max_datestamp(cursor)

    api = VkcApi()
    records, token, total = api.list_records(from_filter=last_synced)
    total_count = len(records)

    while len(records) > 0:
        progress = round((total_count/total)*100, 1)

        print(f"Saving {len(records)} of {total} records {progress} %")
        for record in records:
            if record['work_id'] is not None:
                # for a few records, work_id is missing, we omit these
                HarvestTable.insert(cursor, record)

        conn.commit()  # commit batch of inserts

        if total_count >= total:
            break  # exit loop, we have all records from vkc

        # fetch next batch of records with api
        records, token, total = api.list_records(resumptionToken=token)
        total_count += len(records)

    cursor.close()
    conn.close()


def harvest_vkc(**context):
    print(f"harvest_vkc called. context={context}")
    params = context.get('params', {})
    full_sync = params.get('full_sync', False)

    if full_sync:
        print("VKC full sync started...")
        HarvestTable.truncate(
            PostgresHook(postgres_conn_id=DB_CONNECT_ID).get_conn()
        )
    else:
        print("VKC delta sync started...")

    synchronize_vkc()


def harvest_mapping(**context):
    print(f'harvest_mapping called, context={context}')
    mh_api = MediahavenApi()
    db_connection = PostgresHook(postgres_conn_id=DB_CONNECT_ID).get_conn()

    # find all possible images with inventaris nr's and store in hashtable:
    params = context.get('params', {})
    full_sync = params.get('full_sync', False)
    mh_api.build_lookup_table(db_connection, full_sync)

    db_connection.commit()
    db_connection.close()


def transform_xml(**context):
    print(f'transform_xml called, context={context}')
    # tr = XmlTransformer()

    # Notice: using server cursor, makes batches work
    # we open a second connection and cursor to do our update calls
    read_conn = PostgresHook(postgres_conn_id=DB_CONNECT_ID).get_conn()
    update_conn = PostgresHook(postgres_conn_id=DB_CONNECT_ID).get_conn()

    transform_count = 0
    transform_total = HarvestTable.transform_count(read_conn)
    print(f"Now transforming {transform_total} xml records...")

    rc = read_conn.cursor('serverCursor', cursor_factory=DictCursor)
    HarvestTable.batch_select_transform_records(rc)
    while True:
        records = rc.fetchmany(size=BATCH_SIZE)
        if not records:
            break

        transform_count += len(records)
        progress = round((transform_count/transform_total)*100, 1)
        uc = update_conn.cursor(cursor_factory=DictCursor)

        # use forked process to convert a whole batch of records
        # we can revert to using tr.convert once the saxonc memory leak
        # is fixed. For now converting a batch and then closing the forked
        # process and starting a new one seems to work well
        xpos = 0
        vkc_xml_batch = [record['vkc_xml'] for record in records]
        mam_xml_batch = xml_convert(vkc_xml_batch)

        for record in records:
            # mam_xml = tr.convert(record['vkc_xml'])
            mam_xml = mam_xml_batch[xpos]
            print("updating xml for work_id {}, fragment_id {}, cp_id {}".format(
                record['work_id'],
                record['fragment_id'],
                record['cp_id']
            ))
            HarvestTable.update_mam_xml(uc, record, mam_xml)
            xpos += 1

        update_conn.commit()  # commit all updates current batch
        uc.close()
        print(f"Processed {len(records)} records, progress {progress} %")

    rc.close()
    read_conn.close()
    update_conn.close()


def push_to_rabbitmq(**context):
    print(f'push_to_rabbitmq called, context={context}')
    rp = RabbitPublisher()
    read_conn = PostgresHook(postgres_conn_id=DB_CONNECT_ID).get_conn()
    update_conn = PostgresHook(postgres_conn_id=DB_CONNECT_ID).get_conn()

    publish_count = 0
    publish_total = HarvestTable.publish_count(read_conn)
    print(f"Now sending {publish_total} mam xml records...")

    rc = read_conn.cursor('serverCursor', cursor_factory=DictCursor)
    HarvestTable.batch_select_publish_records(rc)
    while True:
        records = rc.fetchmany(size=BATCH_SIZE)
        if not records:
            break

        print(f"Fetched {len(records)} records, pushing on rabbitmq...")
        uc = update_conn.cursor(cursor_factory=DictCursor)
        for record in records:
            rp.publish(record)
            HarvestTable.set_synchronized(uc, record, True)

        publish_count += len(records)
        progress = round((publish_count/publish_total)*100, 1)
        print(f"Published {len(records)} records, progress {progress} %")

        update_conn.commit()  # commit all updates current batch
        uc.close()

    rc.close()
    read_conn.close()


with dag:
    # postgres_default is defined in the admin/connections
    # find+update the entry in the airflow database.
    create_harvest_table = PostgresOperator(
        task_id="create_harvest_table",
        postgres_conn_id=DB_CONNECT_ID,
        sql=HarvestTable.create_sql()
    )

    create_mapping_table = PostgresOperator(
        task_id="create_mapping_table",
        postgres_conn_id=DB_CONNECT_ID,
        sql=MappingTable.create_sql()
    )

    harvest_vkc_task = PythonOperator(
        task_id='harvest_vkc',
        python_callable=harvest_vkc,
        # op_kwargs={'full_sync': True}
    )

    harvest_mapping_task = PythonOperator(
        task_id='harvest_mapping',
        python_callable=harvest_mapping,
    )

    transform_xml_task = PythonOperator(
        task_id='transform_xml',
        python_callable=transform_xml,
    )

    push_to_rabbitmq_task = PythonOperator(
        task_id='push_to_rabbitmq',
        python_callable=push_to_rabbitmq,
    )

    create_harvest_table >> create_mapping_table >> \
        harvest_vkc_task >> harvest_mapping_task >> \
        transform_xml_task >> push_to_rabbitmq_task
