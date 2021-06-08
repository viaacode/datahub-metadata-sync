import unittest
from airflow.dags.task_services.harvest_vkc_job import harvest_vkc_job
from datetime import datetime
from mock_database import MockDatabase

# TODO: with these fixtures we can now use request recording
# the database stuff is ok, now we want to also mock responses
# from the vkc_api
def harvest_vkc_delta_fixture():
    return [
        {
            'qry': 'SELECT count(*)',
            'rows': [2]
        },
        {
            'qry': 'SELECT max(datestamp)',
            'rows': [datetime(2021, 5, 26, 23, 18, 12)]  # gives back 3 results
            # [datetime(2021, 5, 26, 23, 18, 22)] # returns 1 last vkc entry
        }
    ]


def harvest_vkc_full_fixture():
    return [
        {
            'qry': 'SELECT count(*)',
            'rows': [2]
        },
        {
            'qry': 'SELECT max(datestamp)',
            'rows': [datetime(2021, 5, 26, 23, 18, 22)]  # 1 last vkc entry
            # [] for full sync (but we will first do the vcr recording)
        }
    ]


class TestHarvestVkcJob(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.testdb = MockDatabase()

    def test_harvest_job_fullsync(self):
        self.testdb.set_fixtures(harvest_vkc_full_fixture())
        harvest_vkc_job(self.testdb, True)
        assert 'TRUNCATE TABLE harvest_vkc' in self.testdb.qry_history()
        assert self.testdb.close_count == 1
        assert self.testdb.commit_count == 2 

    def test_harvest_job_delta(self):
        self.testdb.set_fixtures(harvest_vkc_delta_fixture())
        harvest_vkc_job(self.testdb, False)
        assert 'TRUNCATE TABLE harvest_vkc' not in self.testdb.qry_history()
        assert self.testdb.close_count == 1
        assert self.testdb.commit_count == 1


