import pytest
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
            'rows': [datetime(2021, 5, 26, 23, 18, 22)]  # 1 last vkc entry
            # 'rows': [datetime(2021, 5, 26, 23, 18, 12)]  # gives back 3 results
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
            'rows': [] # real full sync returns no datestamp
            # in our yaml file this is using from_filter = '2011-06-01T00:00:00Z'
            # 'rows': [datetime(2021, 5, 26, 23, 18, 1)]  # gives back +-12 results
        }
    ]


pytestmark = [pytest.mark.vcr(ignore_localhost=True)]


@pytest.fixture(scope="module")
def vcr_config():
    # important to add the filter_headers here to avoid exposing credentials
    # in tests/cassettes!
    return {
        "record_mode": "once",
        "decode_compressed_response": True,
        "filter_headers": ["authorization"]
    }


@pytest.mark.vcr
def test_harvest_job_fullsync():
    # set up mocked database connection with fixture data
    testdb = MockDatabase(harvest_vkc_full_fixture())

    # run harvest_vkc_job full sync
    harvest_vkc_job(testdb, True)

    assert 'TRUNCATE TABLE harvest_vkc' in testdb.qry_history()
    assert testdb.close_count == 1
    assert testdb.commit_count == 2


@pytest.mark.vcr
def test_harvest_job_delta():
    # set up mocked database connection with fixture data
    testdb = MockDatabase(harvest_vkc_delta_fixture())

    # run delta sync
    harvest_vkc_job(testdb, False)

    assert 'TRUNCATE TABLE harvest_vkc' not in testdb.qry_history()
    assert testdb.close_count == 1
    assert testdb.commit_count == 1
