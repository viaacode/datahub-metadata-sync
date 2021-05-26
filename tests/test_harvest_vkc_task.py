#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest
from unittest.mock import patch, Mock, MagicMock
from airflow import DAG
from airflow.dags.vkc_oai_harvester import harvest_vkc
from airflow.models.taskinstance import TaskInstance
from airflow.operators.python import PythonOperator
from datetime import datetime

   

DEFAULT_DATE = '2021-05-01'
TEST_DAG_ID = 'vkc_oai_harvester'

# attempt at mocking postgres. TODO: further tweak this for our setup...
# this uses a seperate docker for postgres queries
from collections import namedtuple
from pytest_docker_tools import container, fetch

@pytest.fixture(scope="module")
def postgres_credentials():
    PostgresCredentials = namedtuple("PostgresCredentials", ["username", "password"])
    return PostgresCredentials("testuser", "testpass")

postgres_image = fetch(repository="postgres:11.1-alpine")
postgres = container(
    image="{postgres_image.id}",
    environment={
        "POSTGRES_USER": "{postgres_credentials.username}",
        "POSTGRES_PASSWORD": "{postgres_credentials.password}",
    },
    ports={"5432/tcp": None},
    volumes={
        path.join(path.dirname(__file__), "postgres-init.sql"): {
            "bind": "/docker-entrypoint-initdb.d/postgres-init.sql"
        }
    },
)

class HarvestVkcTest(unittest.TestCase):

    def setUp(self):
        self.dag = DAG(
            TEST_DAG_ID,
            schedule_interval='@daily',
            default_args={'start_date': DEFAULT_DATE}
        )

        self.op = PythonOperator(
            dag=self.dag,
            task_id='harvest_vkc',
            python_callable=harvest_vkc,
            op_kwargs={'full_sync': False}
        )
        self.ti = TaskInstance(
            task=self.op,
            execution_date=datetime.strptime(DEFAULT_DATE, '%Y-%m-%d')
        )

    # TODO: mock vkc retrieval (currently makes real connection)
    # TODO: mock out database connection
    def test_harvest_execution(self):
        context = self.ti.get_template_context()
        self.op.prepare_for_execution().execute(context)

        assert self.op.retries == 0
        assert not self.op.op_kwargs['full_sync']
