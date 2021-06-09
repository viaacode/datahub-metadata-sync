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
from airflow.dags.task_services.transform_xml_job import transform_xml_job
from mock_database import MockDatabase

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
                'qry': 'SELECT harvest_vkc.id, harvest_vkc.mam_xml, harvest_vkc.vkc_xml',
                'rows': [
                    {
                        'id': 1,
                        'work_id': 'T2023.065-1',
                        'vkc_xml': load_xml('vkc_doc1.xml')
                    },
                    {
                        'id': 2,
                        'work_id': '4030/3',
                        'vkc_xml': load_xml('vkc_doc2.xml')
                    },
                    {
                        'id': 3,
                        'work_id': '4039/3',
                        'vkc_xml': load_xml('vkc_doc3.xml')
                    },
                    {
                        'id': 4,
                        'work_id': '4037/6',
                        'vkc_xml': load_xml('vkc_doc4.xml')
                    },
                    {
                        'id': 5,
                        'work_id': '4045/3',
                        'vkc_xml': load_xml('vkc_doc5.xml')
                    }
                ]
            }
        ]
    }


@mock.patch('airflow.dags.task_services.transform_xml_job.BATCH_SIZE', 3)
def test_xml_transformations():
    # set up mocked database connection with fixture data
    read_conn = MockDatabase(transform_xml_fixture())
    update_conn = MockDatabase()

    transform_xml_job(read_conn, update_conn)

    assert read_conn.commit_count == 0
    assert update_conn.commit_count == 1

    # TODO: add output fixtures mam_doc1.xml .. mam_doc5.xml
    # TODO: use load_xml('mam_doc1.xml') ...
    assert 'UPDATE harvest_vkc' in update_conn.qry_history()[0]
    assert 'UPDATE harvest_vkc' in update_conn.qry_history()[1]
    assert 'UPDATE harvest_vkc' in update_conn.qry_history()[2]
    assert 'UPDATE harvest_vkc' in update_conn.qry_history()[3]
    assert 'UPDATE harvest_vkc' in update_conn.qry_history()[4]

    assert read_conn.close_count == 1
    assert update_conn.close_count == 1
