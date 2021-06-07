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

from task_services.harvest_table import HarvestTable
from task_services.mapping_table import MappingTable

from task_services.harvest_vkc_job import harvest_vkc_job
from task_services.harvest_mapping_job import harvest_mapping_job
from task_services.transform_xml_job import transform_xml_job
from task_services.publish_updates_job import publish_updates_job

from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
# from psycopg2.extras import DictCursor

DB_CONNECT_ID = 'postgres_default'

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


# when triggering dag you can pass in json configuration
# for full sync by entering the following in optional json config:
# {"full_sync": true}
# then press the trigger button
def harvest_vkc(**context):
    print(f"harvest_vkc called. context={context}")
    params = context.get('params', {})
    full_sync = params.get('full_sync', False)

    # fetch all vkc records with api and store in db table
    harvest_vkc_job(
        PostgresHook(postgres_conn_id=DB_CONNECT_ID).get_conn(),
        full_sync
    )


def harvest_mapping(**context):
    print(f'harvest_mapping called, context={context}')
    params = context.get('params', {})
    full_sync = params.get('full_sync', False)

    harvest_mapping_job(
        PostgresHook(postgres_conn_id=DB_CONNECT_ID).get_conn(),
        full_sync
    )


def transform_xml(**context):
    print(f'transform_xml called, context={context}')
    read_conn = PostgresHook(postgres_conn_id=DB_CONNECT_ID).get_conn()
    update_conn = PostgresHook(postgres_conn_id=DB_CONNECT_ID).get_conn()

    transform_xml_job(read_conn, update_conn)


def push_to_rabbitmq(**context):
    print(f'push_to_rabbitmq called, context={context}')
    read_conn = PostgresHook(postgres_conn_id=DB_CONNECT_ID).get_conn()
    update_conn = PostgresHook(postgres_conn_id=DB_CONNECT_ID).get_conn()

    publish_updates_job(read_conn, update_conn)


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
