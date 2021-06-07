import unittest
from airflow import DAG
from airflow.dags.vkc_oai_harvester import harvest_mapping
# from airflow.dags.task_services.mapping_table import MappingTable

from airflow.models.taskinstance import TaskInstance
from airflow.operators.python import PythonOperator
# from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.providers.sqlite.operators.sqlite import SqliteOperator

from datetime import datetime
# from airflow.models import DagBag
# from airflow.utils.state import State

from unittest import mock


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

            # the only way we can get this to work for now,
            # we skipped the created_at, updated_at to see if
            # this properly creates our db and further executes our dag task.

            # sql=MappingTable.create_sql()
            # created_at INTEGER DEFAULT datetime('now','unixepoch'),
            # updated_at INTEGER DEFAULT datetime('now','unixepoch')
            sql="""
            CREATE TABLE IF NOT EXISTS mapping_vkc(
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
        # create our mapping_vkc table in the airflow/airflow.db sqlite3 db
        context = self.ti_table.get_template_context()
        self.create_mapping_op.prepare_for_execution().execute(context)

        # TODO: mock the postgres connect somehow to work on sqlite also here
        context = self.ti.get_template_context()
        self.mapping_op.prepare_for_execution().execute(context)
        # assert self.ti.state == State.SUCCESS
        assert self.mapping_op.retries == 0
        assert not self.mapping_op.op_kwargs['full_sync']

    @mock.patch('airflow.providers.postgres.hooks.postgres.PostgresHook')
    def test_mock_hook(self, mock_postgres):
        mock_postgres().__enter__().cursor().__enter__().fetchall.return_value = ['Walter']

        # now call our harvest_vkc method with mocked mapping.
        context = self.ti.get_template_context()
        self.mapping_op.prepare_for_execution().execute(context)

        record = {
            'work_id': 12,
            'xml': '<xml></xml>',
            'datestamp': datetime.now(),
            'aanbieder': 'aanbieder hier',
            'min_breedte_cm': '233',
            'max_breedte_cm': '244'
        }

        # __import__('pdb').set_trace()
        # mock_postgres().cursor().execute.assert_called_with(
        mock_postgres().__enter__().cursor().__enter__().execute.assert_called_with(
            """
            INSERT INTO harvest_vkc (
                work_id, vkc_xml, mam_xml, datestamp,
                aanbieder, min_breedte_cm, max_breedte_cm
            )
            VALUES(%s, %s, NULL, %s, %s, %s, %s)
            """,
            (
                record['work_id'], record['xml'], record['datestamp'],
                record['aanbieder'], record['min_breedte_cm'],
                record['max_breedte_cm']
            )
        )



# here we now see we need our wrapper instead of directly using
# postgreshooks in our dag code
#     def test_execute_no_trigger(self):
#         self.ti.run(ignore_ti_state=True)
#         assert self.ti.state == State.SUCCESS
#         # Assert something related to tasks results




# in harvest mapping insert this to debug above mocking...
#     record = {
#             'work_id': 12,
#             'xml': '<xml></xml>',
#             'datestamp': datetime.now(),
#             'aanbieder': 'aanbieder hier',
#             'min_breedte_cm': '233',
#             'max_breedte_cm': '244'
#     }
#     HarvestTable.insert(cursor, record)


