import unittest
from airflow import DAG
from airflow.dags.vkc_oai_harvester import harvest_mapping
from airflow.models.taskinstance import TaskInstance
from airflow.operators.python import PythonOperator
from datetime import datetime
# from airflow.models import DagBag
# from airflow.utils.state import State


DEFAULT_DATE = '2021-05-01'
TEST_DAG_ID = 'vkc_oai_harvester'


class HarvestMappingTest(unittest.TestCase):

    def setUp(self):
        self.dag = DAG(
            TEST_DAG_ID,
            schedule_interval='@daily',
            default_args={'start_date': DEFAULT_DATE}
        )

        self.op = PythonOperator(
            dag=self.dag,
            task_id='harvest_mapping',
            python_callable=harvest_mapping,
            op_kwargs={'full_sync': False}
        )
        self.ti = TaskInstance(
            task=self.op,
            execution_date=datetime.strptime(DEFAULT_DATE, '%Y-%m-%d')
        )

    # TODO: stub out the mh_api call for list and return smaller subset.
    # TODO: mock out database connection
    def test_harvest_mapping_execution(self):
        context = self.ti.get_template_context()
        self.op.prepare_for_execution().execute(context)
        # assert self.ti.state == State.SUCCESS
        assert self.op.retries == 0
        assert not self.op.op_kwargs['full_sync']


#   def test_execute_no_trigger(self):
#       self.ti.run(ignore_ti_state=True)
#       assert self.ti.state == State.SUCCESS
#       # Assert something related to tasks results
