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
import os
from unittest import mock
from airflow.dags.task_services.publish_updates_job import publish_updates_job
from mock_database import MockDatabase
from mock_rabbit import MockRabbitClient

pytestmark = [pytest.mark.vcr(ignore_localhost=True)]


def load_xml(name):
    currentdir = os.path.dirname(os.path.abspath(__file__))
    print(f"current_dir={currentdir}")
    filepath = os.path.join(currentdir, "fixtures", name)
    print(f"filepath={filepath}")

    with open(filepath, "r") as xmlfile:
        return xmlfile.read()


def transform_xml_fixture():
    return {
        'fetchone': [
            {
                'qry': 'SELECT count(*)',
                'rows': [5]
            },
        ],
        'fetchmany': [
            {
                # HarvestTable.select_transform_records_qry()
                'qry': 'SELECT harvest_vkc.id, harvest_vkc.mam_xml, harvest_vkc.vkc_xml',
                'rows': [
                    {
                        'id': 1,
                        'work_id': 'T2023.065-1',
                        'vkc_xml': load_xml('vkc_doc1.xml'),
                        'mam_xml': load_xml('mam_doc1.xml'),
                        'fragment_id': 'fragment1',
                        'cp_id': 'OR-1testd'
                    },
                    {
                        'id': 2,
                        'work_id': '4030/3',
                        'vkc_xml': load_xml('vkc_doc2.xml'),
                        'mam_xml': load_xml('mam_doc2.xml'),
                        'fragment_id': 'fragment2',
                        'cp_id': 'OR-1testd'
                    },
                    {
                        'id': 3,
                        'work_id': '4039/3',
                        'vkc_xml': load_xml('vkc_doc3.xml'),
                        'mam_xml': load_xml('mam_doc3.xml'),
                        'fragment_id': 'fragment3',
                        'cp_id': 'OR-2testd'
                    },
                    {
                        'id': 4,
                        'work_id': '4037/6',
                        'vkc_xml': load_xml('vkc_doc4.xml'),
                        'mam_xml': load_xml('mam_doc4.xml'),
                        'fragment_id': 'fragment4',
                        'cp_id': 'OR-2testd'
                    },
                    {
                        'id': 5,
                        'work_id': '4045/3',
                        'vkc_xml': load_xml('vkc_doc5.xml'),
                        'mam_xml': load_xml('mam_doc5.xml'),
                        'fragment_id': 'fragment5',
                        'cp_id': 'OR-2testd'
                    }
                ]
            }
        ]
    }


@mock.patch('airflow.dags.task_services.publish_updates_job.BATCH_SIZE', 3)
@mock.patch('airflow.dags.task_services.publish_updates_job.RabbitClient')
def test_publish_updates_job(mock_rc):
    test_rabbit = MockRabbitClient()
    mock_rc.return_value = test_rabbit

    # set up mocked database connection with fixture data
    read_conn = MockDatabase(transform_xml_fixture())
    update_conn = MockDatabase()

    publish_updates_job(read_conn, update_conn)

    assert read_conn.commit_count == 0
    assert update_conn.commit_count == 1

    assert 'SET synchronized = True' in update_conn.qry_history()[0]
    assert 'WHERE id=1' in update_conn.qry_history()[0]

    assert 'SET synchronized = True' in update_conn.qry_history()[1]
    assert 'WHERE id=2' in update_conn.qry_history()[1]

    assert 'SET synchronized = True' in update_conn.qry_history()[2]
    assert 'WHERE id=3' in update_conn.qry_history()[2]

    assert 'SET synchronized = True' in update_conn.qry_history()[3]
    assert 'WHERE id=4' in update_conn.qry_history()[3]

    assert 'SET synchronized = True' in update_conn.qry_history()[4]
    assert 'WHERE id=5' in update_conn.qry_history()[4]

    assert read_conn.close_count == 1
    assert update_conn.close_count == 1

    assert len(test_rabbit.publish_history) == 5

    assert test_rabbit.publish_history[0]['work_id'] == 'T2023.065-1'
    assert test_rabbit.publish_history[0]['fragment_id'] == 'fragment1'
    assert test_rabbit.publish_history[0]['cp_id'] == 'OR-1testd'
    assert test_rabbit.publish_history[0]['mam_xml'] == load_xml(
        'mam_doc1.xml')

    assert test_rabbit.publish_history[1]['mam_xml'] == load_xml(
        'mam_doc2.xml')
    assert test_rabbit.publish_history[2]['mam_xml'] == load_xml(
        'mam_doc3.xml')
    assert test_rabbit.publish_history[3]['mam_xml'] == load_xml(
        'mam_doc4.xml')
    assert test_rabbit.publish_history[4]['mam_xml'] == load_xml(
        'mam_doc5.xml')

    # assert test_rabbit.publish_history[0]['correlation_id'] == 'T2023.065-1'
    # assert test_rabbit.publish_history[0]['fragment_id'] == 'fragment1'
    # assert test_rabbit.publish_history[0]['cp_id'] == 'OR-1testd'
    # assert test_rabbit.publish_history[0]['data'] == load_xml('mam_doc1.xml')
