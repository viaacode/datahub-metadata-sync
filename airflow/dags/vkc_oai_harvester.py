#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  @Author: Walter Schreppers
#
#   airflow/dags/vkc_oai_harvester.py
#
#   DAG with tasks for harvesting and converting OAI data from
#   Vlaamse Kunst Collectie to target MAM and publish via RabbitMQ

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago

from task_services.vkc_api import VkcApi
from task_services.xml_transformer import XmlTransformer
from task_services.rabbit_publisher import RabbitPublisher
from task_services.mediahaven_api import MediahavenApi
from task_services.harvest_table import HarvestTable

from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from psycopg2.extras import DictCursor
from datetime import timezone


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


def vkc_full_sync():
    print("VKC full sync")
    conn = PostgresHook(postgres_conn_id=DB_CONNECT_ID).get_conn()
    cursor = conn.cursor(cursor_factory=DictCursor)

    HarvestTable.truncate(cursor)
    conn.commit()

    api = VkcApi()
    records, token, total = api.list_records()
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


def vkc_delta_sync():
    conn = PostgresHook(postgres_conn_id=DB_CONNECT_ID).get_conn()
    cursor = conn.cursor(cursor_factory=DictCursor)
    last_synced = HarvestTable.get_max_datestamp(cursor)

    if last_synced is None:
        vkc_full_sync()
        return
    else:
        # the vkc api does not support +01:00 format, convert to utc:
        last_synced = last_synced.astimezone(
            tz=timezone.utc
        ).isoformat().replace("+00:00", "Z")

    print(f"VKC delta sync, last_synced={last_synced}")

    # TODO: refactor out code duplication
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
        vkc_full_sync()
    else:
        vkc_delta_sync()


def transform_xml(**context):
    print(f'transform_xml called, context={context}')
    tr = XmlTransformer()
    mh_api = MediahavenApi()

    # Notice: using server cursor, makes batches work
    # we open a second connection and cursor to do our update calls for eatch batch
    read_conn = PostgresHook(postgres_conn_id=DB_CONNECT_ID).get_conn()
    update_conn = PostgresHook(postgres_conn_id=DB_CONNECT_ID).get_conn()

    rc = read_conn.cursor('serverCursor', cursor_factory=DictCursor)
    HarvestTable.batch_select_records(rc)
    while True:
        records = rc.fetchmany(size=BATCH_SIZE)
        if not records:
            break
        print(f"fetched {len(records)} records, now converting...", flush=True)
        uc = update_conn.cursor(cursor_factory=DictCursor)
        for record in records:
            work_id = record['work_id']
            mh_record = mh_api.find_vkc_record(work_id)
            if mh_record is not None:
                fragment_id = mh_record['Internal']['FragmentId']
                cp_id = mh_record['Dynamic']['CP_id']
                print(
                    f"Record work_id={work_id} found, fragment_id={fragment_id} cp_id={cp_id}")
                converted_record = tr.convert(record[1])
                HarvestTable.update_mam_xml(
                    uc, record, converted_record, fragment_id, cp_id)
            else:
                print(f"Skipping record with work_id={work_id}")

        update_conn.commit()  # commit all updates current batch
        uc.close()

    rc.close()
    read_conn.close()


def push_to_rabbitmq(**context):
    print(f'push_to_rabbitmq called, context={context}')
    rp = RabbitPublisher()

    read_conn = PostgresHook(postgres_conn_id=DB_CONNECT_ID).get_conn()
    update_conn = PostgresHook(postgres_conn_id=DB_CONNECT_ID).get_conn()

    rc = read_conn.cursor('serverCursor', cursor_factory=DictCursor)
    HarvestTable.batch_select_updateable_records(rc)
    while True:
        records = rc.fetchmany(size=BATCH_SIZE)
        if not records:
            break
        print(f"fetched {len(records)} records, pushing on rabbitmq...")
        uc = update_conn.cursor(cursor_factory=DictCursor)
        for record in records:
            rp.publish(record)
            HarvestTable.set_synchronized(uc, record, True)

        update_conn.commit()  # commit all updates current batch
        uc.close()

    rc.close()
    read_conn.close()


with dag:
    # postgres_default is defined in the admin/connections
    # find+update the entry in the airflow database.
    create_db_table = PostgresOperator(
        task_id="create_harvest_table",
        postgres_conn_id=DB_CONNECT_ID,
        sql=HarvestTable.create_sql()
    )

    harvest_vkc_task = PythonOperator(
        task_id='harvest_vkc',
        python_callable=harvest_vkc,
        # op_kwargs={'full_sync': True}
    )

    transform_xml_task = PythonOperator(
        task_id='transform_xml',
        python_callable=transform_xml,
    )

    push_to_rabbitmq_task = PythonOperator(
        task_id='push_to_rabbitmq',
        python_callable=push_to_rabbitmq,
    )

    create_db_table >> harvest_vkc_task >> transform_xml_task >> push_to_rabbitmq_task
