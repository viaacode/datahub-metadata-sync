#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  @Author: Walter Schreppers
#
#  tests/test_harvest_mapping_job.py
#
#   This tests the harvest_mapping_job
#   Harvest mapping collects work_ids from inventaris nummers
#   with mediahaven api calls. And stores the associated fragment_id's
#   this will be used in later jobs.
#
#   We supply some fixture data to our MockDatabase to get good coverage.
#

import pytest
from unittest import mock
from airflow.dags.task_services.harvest_mapping_job import harvest_mapping_job
from airflow.dags.task_services.mapping_table import MappingTable
from datetime import datetime
from mock_database import MockDatabase

pytestmark = [pytest.mark.vcr(ignore_localhost=True)]


def mapping_delta_fixture():
    return {
        'fetchone': [
            {
                'qry': 'SELECT count(*)',
                'rows': [180]
            },
            {
                'qry': 'SELECT max(datestamp)',
                # 1 last vkc entry
                'rows': [datetime(2021, 5, 26, 23, 18, 22)]
                # 'rows': [datetime(2021, 5, 26, 23, 18, 12)]   # gives back 3 results
            }
        ],
        'fetchmany': []
    }


def mapping_full_fixture():
    return {
        'fetchone': [
            {
                'qry': 'SELECT count(*)',
                'rows': [0]
            },
            {
                'qry': 'SELECT max(datestamp)',
                'rows': []  # real full sync returns no datestamp
            }
        ],
        'fetchmany': []
    }


def insert_statement_fixture():
    qry = MappingTable.insert_qry()

    fragment_id = '{}{}{}'.format(
        '352a50c10dcb454495ee0ef481cf019002c2',
        '0da43a3b444184c1603324833f8e918488a4',
        '60064ef4b8f18b353035b4cf'
    )
    return qry % (
        '072_019',          # work_id
        '20160406_0029',    # work_id_alternate
        fragment_id,
        'qsmk654z08',       # exernal_id
        'OR-4t6f29d',       # cp_id
        'image/tiff',       # mimetype
        '5438',             # width_px
        '8367',             # height_px
    )


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
@mock.patch('airflow.dags.task_services.harvest_mapping_job.BATCH_SIZE', 3)
def test_mapping_delta():
    # set up mocked database connection with fixture data
    testdb = MockDatabase(mapping_delta_fixture())

    # run delta sync
    harvest_mapping_job(testdb, full_sync=False)

    assert 'TRUNCATE TABLE mapping_vkc' not in testdb.qry_history()
    assert testdb.close_count == 1
    assert testdb.commit_count == 0


@pytest.mark.vcr
@mock.patch('airflow.dags.task_services.harvest_mapping_job.BATCH_SIZE', 3)
def test_mapping_full():
    # set up mocked database connection with fixture data
    testdb = MockDatabase(mapping_full_fixture())

    # run harvest_vkc_job full sync and patch the batch size to 3
    harvest_mapping_job(testdb, full_sync=True)

    assert 'TRUNCATE TABLE mapping_vkc' in testdb.qry_history()
    assert insert_statement_fixture() in testdb.qry_history()
    assert testdb.close_count == 1
    assert testdb.commit_count == 11
