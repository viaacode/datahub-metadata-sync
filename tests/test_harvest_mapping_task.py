import unittest
from airflow import DAG
from airflow.dags.vkc_oai_harvester import harvest_mapping
from airflow.dags.task_services.mapping_table import MappingTable

from airflow.models.taskinstance import TaskInstance
from airflow.operators.python import PythonOperator
#from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.providers.sqlite.operators.sqlite import SqliteOperator 

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

        self.create_mapping_op = SqliteOperator(
            dag=self.dag,
            task_id='create_mapping_table',
            sqlite_conn_id='postgres_default',  # DB_CONNECT_ID
            # sql=MappingTable.create_sql()
            # CREATE TABLE IF NOT EXISTS mapping_vkc(
            # created_at INTEGER DEFAULT datetime('now','unixepoch'),
            # updated_at INTEGER DEFAULT datetime('now','unixepoch')
            sql="""
            CREATE TABLE mapping_vkc (
                id INTEGER PRIMARY KEY,
                work_id TEXT,
                work_id_alternate TEXT,
                fragment_id TEXT,
                external_id TEXT,
                cp_id TEXT,
                mimetype TEXT,
                width_px INTEGER,
                height_px INTEGER
            );
            """
        )
        self.ti_table = TaskInstance(
            task=self.create_mapping_op,
            execution_date=datetime.strptime(DEFAULT_DATE, '%Y-%m-%d')
        )

        self.mapping_op = PythonOperator(
            dag=self.dag,
            task_id='harvest_mapping',
            python_callable=harvest_mapping,
            op_kwargs={'full_sync': False}
        )
        self.ti = TaskInstance(
            task=self.mapping_op,
            execution_date=datetime.strptime(DEFAULT_DATE, '%Y-%m-%d')
        )

    # TODO: stub out the mh_api call for list and return smaller subset.
    # database is now airflow/airflow.db sqlite for testing
    def test_harvest_mapping_execution(self):
        context = self.ti_table.get_template_context()
        self.create_mapping_op.prepare_for_execution().execute(context)
 
        context = self.ti.get_template_context()
        self.mapping_op.prepare_for_execution().execute(context)
        # assert self.ti.state == State.SUCCESS
        assert self.mapping_op.retries == 0
        assert not self.mapping_op.op_kwargs['full_sync']


#   def test_execute_no_trigger(self):
#       self.ti.run(ignore_ti_state=True)
#       assert self.ti.state == State.SUCCESS
#       # Assert something related to tasks results
