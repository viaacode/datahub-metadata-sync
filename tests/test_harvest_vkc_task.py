import unittest
import pytest
from airflow.utils.state import State
from airflow import DAG
from airflow.dags.vkc_oai_harvester import harvest_vkc
from airflow.models.taskinstance import TaskInstance
from airflow.operators.python import PythonOperator
from datetime import datetime
from airflow.models import DagBag


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

