#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  @Author: Walter Schreppers
#
#  tests/test_transform_xml_job.py
#
#   This tests the xml transformation task
#   We supply a fixture for harvesttable with MockDatabase
#   the job iterates this fixture, gets the xml samples and converts them
#   we check the output of converted xml
#

import pytest
from unittest import mock
from airflow.dags.task_services.transform_xml_job import transform_xml_job
from airflow.dags.task_services.harvest_table import HarvestTable
from datetime import datetime
from mock_database import MockDatabase

pytestmark = [pytest.mark.vcr(ignore_localhost=True)]


def transform_xml_fixture():
    return {
        'fetchone': [
            {
                'qry': 'SELECT count(*)',
                'rows': [5]
            },
            {
                'qry': 'SELECT max(datestamp)',
                'rows': [datetime(2021, 5, 26, 23, 18, 22)]  # TODO CHANGE THIS
            }
        ],
        'fetchmany': [
            {
                'qry': 'SELECT harvest_vkc.id, harvest_vkc.mam_xml, harvest_vkc.vkc_xml',
                'rows': [
                    {
                        'id': 1,
                        'work_id': '123',
                        'vkc_xml': 'some xmldoc here'  # TODO: actual valid XML HERE!
                    },
                    {
                        'id': 2,
                        'work_id': '345',
                        'vkc_xml': 'some other doc here'  # TODO: valid XML here!
                    }
                ]
            }
        ]
    }


def insert_statement_fixture():
    qry = HarvestTable.insert_qry()

    fragment_id = '{}{}{}'.format(
        '352a50c10dcb454495ee0ef481cf019002c2',
        '0da43a3b444184c1603324833f8e918488a4',
        '60064ef4b8f18b353035b4cf'
    )
    return qry % (
        'val1',       # col name
        'val2',       #
        fragment_id,  # TODO: figure out position of this...
    )


@pytest.mark.skip(reason="we need valid xml data in above fixture")
@mock.patch('airflow.dags.task_services.transform_xml_job.BATCH_SIZE', 3)
def test_xml_transformations():
    # set up mocked database connection with fixture data
    read_conn = MockDatabase(transform_xml_fixture())
    update_conn = MockDatabase()

    transform_xml_job(read_conn, update_conn)

    assert read_conn.close_count == 1
    assert update_conn.close_count == 1

    assert read_conn.commit_count == 0
    assert update_conn.commit_count == 5
    assert 'TRUNCATE TABLE harvest_vkc' in update_conn.qry_history()
    # TODO: more asserts here!
