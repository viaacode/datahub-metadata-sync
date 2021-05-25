import unittest
from airflow import DAG
from airflow.dags.vkc_oai_harvester import transform_xml
from airflow.models.taskinstance import TaskInstance
from airflow.operators.python import PythonOperator
from datetime import datetime


DEFAULT_DATE = '2021-05-01'
TEST_DAG_ID = 'vkc_oai_harvester'


class TransformXmlTest(unittest.TestCase):

    def setUp(self):
        self.dag = DAG(
            TEST_DAG_ID,
            schedule_interval='@daily',
            default_args={'start_date': DEFAULT_DATE}
        )

        self.op = PythonOperator(
            dag=self.dag,
            task_id='transform_xml',
            python_callable=transform_xml,
            op_kwargs={'full_sync': False}
        )
        self.ti = TaskInstance(
            task=self.op,
            execution_date=datetime.strptime(DEFAULT_DATE, '%Y-%m-%d')
        )

    # TODO: mock out database connection
    def test_transform_execution(self):
        context = self.ti.get_template_context()
        self.op.prepare_for_execution().execute(context)
        assert self.op.retries == 0
        assert not self.op.op_kwargs['full_sync']
