import unittest
import pytest
from airflow import DAG
from airflow.dags.vkc_oai_harvester import push_to_rabbitmq
from airflow.models.taskinstance import TaskInstance
from airflow.operators.python import PythonOperator
from datetime import datetime


DEFAULT_DATE = '2021-05-01'
TEST_DAG_ID = 'vkc_oai_harvester'


class HarvestVkcTest(unittest.TestCase):

    def setUp(self):
        self.dag = DAG(
            TEST_DAG_ID,
            schedule_interval='@daily',
            default_args={'start_date': DEFAULT_DATE}
        )

        self.op = PythonOperator(
            dag=self.dag,
            task_id='push_to_rabbitmq',
            python_callable=push_to_rabbitmq,
            op_kwargs={'full_sync': False}
        )
        self.ti = TaskInstance(
            task=self.op,
            execution_date=datetime.strptime(DEFAULT_DATE, '%Y-%m-%d')
        )

    # TODO: mock out rabbit mq connection

    @pytest.mark.skip(reason='rabbit mq connection needs mocking')
    def test_push_to_rabbit(self):
        context = self.ti.get_template_context()
        self.op.prepare_for_execution().execute(context)

        assert self.op.retries == 0
        assert not self.op.op_kwargs['full_sync']
