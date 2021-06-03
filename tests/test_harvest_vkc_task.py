#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# import pytest
# from os import path
from unittest import mock, TestCase

from airflow import DAG
from airflow.dags.vkc_oai_harvester import harvest_vkc
from airflow.models.taskinstance import TaskInstance
from airflow.operators.python import PythonOperator
from datetime import datetime

# attempt at mocking postgres. TODO: further tweak this for our setup...
# this uses a seperate docker for postgres queries
# from collections import namedtuple
# from pytest_docker_tools import container, fetch


DEFAULT_DATE = '2021-05-01'
TEST_DAG_ID = 'vkc_oai_harvester'


# @pytest.fixture(scope="module")
# def postgres_credentials():
#     PostgresCredentials = namedtuple("PostgresCredentials", ["username", "password"])
#     return PostgresCredentials("testuser", "testpass")
#
#
# postgres_image = fetch(repository="postgres:11.1-alpine")
# postgres = container(
#     image="{postgres_image.id}",
#     environment={
#         "POSTGRES_USER": "{postgres_credentials.username}",
#         "POSTGRES_PASSWORD": "{postgres_credentials.password}",
#     },
#     ports={"5432/tcp": None},
#     volumes={
#         path.join(path.dirname(__file__), "postgres-init.sql"): {
#             "bind": "/docker-entrypoint-initdb.d/postgres-init.sql"
#         }
#     },
# )


class HarvestVkcTest(TestCase):

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

#     # TODO: mock vkc retrieval (currently makes real connection)
#     # TODO: mock out database connection
#     def test_harvest_execution(self):
#         context = self.ti.get_template_context()
#         self.op.prepare_for_execution().execute(context)
#
#         assert self.op.retries == 0
#         assert not self.op.op_kwargs['full_sync']
#

    @mock.patch("psycopg2.connect")
    @mock.patch("psycopg2.extras.register_uuid")
    @mock.patch("psycopg2.extensions.register_type")
    def test_harvest_execution(self, mock_connect, mock_register_uuid, mock_register_type):
        expected = [['fake', 'row', 1], ['fake', 'row', 2]]
        # result of psycopg2.connect(**connection_stuff)
        mock_con = mock_connect.return_value

        # mock_con.server_version = 90401
        # mock_con.info.server_version = 90401

        mock_info = mock.MagicMock()
        mock_info.version.return_value = 90401
        mock_con.info.return_value = mock_info

        mock_con.on_connect.return_value = mock.MagicMock()
        # result of con.cursor(cursor_factory=DictCursor)
        mock_cur = mock_con.cursor.return_value
        # return this when calling cur.fetchall()
        mock_cur.fetchall.return_value = expected

        # mock_register_uuid = mock.MagicMock()  # mock out the register_uuid
        # mock_register_type = mock.MagicMock()  # mock out the register_uuid
        # self.op.CONN = mock_con

        # mock_cursor = mock.MagicMock()
        # mock_cursor.fetchone.return_value = {
        #       "id": 1,
        #       "name": "Bob",
        #       "age": 25
        # }
        # mock_connect.cursor.return_value.__enter__.return_value = mock_cursor
        # mock_cursor.on_connect.return_value = mock.MagicMock()

        # self.op.CONN = mock_connect

        # mock_register_uuid = mock.MagicMock() #mock out the register_uuid
        # mock_on_connect = mock.MagicMock()

        context = self.ti.get_template_context()
        self.op.prepare_for_execution().execute(context)

        assert self.op.retries == 0
        assert not self.op.op_kwargs['full_sync']

        # result = super_cool_method()
        # self.assertEqual(result, expected)
