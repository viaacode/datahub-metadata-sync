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
from airflow.dags.task_services.harvest_table import HarvestTable
from mock_database import MockDatabase

pytestmark = [pytest.mark.vcr(ignore_localhost=True)]


def load_xml(name):
    currentdir = os.path.dirname(os.path.abspath(__file__))
    filepath = os.path.join(currentdir, "fixtures", name)

    with open(filepath, "r") as xmlfile:
        return xmlfile.read()


def transform_xml_fixture():
    return {
        'fetchone': [
            {
                'qry': 'SELECT COUNT(DISTINCT harvest_vkc.id)',
                'rows': [5]
            },
        ],
        'fetchmany': [
            {
                'qry': 'SELECT DISTINCT ON (harvest_vkc.id) harvest_vkc.id, harvest_vkc.work_id',
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


def update_mam_qry(record_id, xml_fixture):
    mam_xml = load_xml(xml_fixture)
    update_qry = HarvestTable.update_mam_xml_qry() % (
        mam_xml,
        record_id
    )

    return update_qry


def compare_query(a, b):
    return [c for c in a if c.isalpha()] == [c for c in b if c.isalpha()]


@mock.patch('airflow.dags.task_services.transform_xml_job.BATCH_SIZE', 3)
def test_xml_transformations():
    # set up mocked database connection with fixture data
    read_conn = MockDatabase(transform_xml_fixture())
    update_conn = MockDatabase()

    transform_xml_job(read_conn, update_conn)

    assert read_conn.commit_count == 0
    assert update_conn.commit_count == 1

    assert compare_query(update_mam_qry(1, 'mam_doc1.xml'),
                         update_conn.qry_history()[0])
    assert compare_query(update_mam_qry(2, 'mam_doc2.xml'),
                         update_conn.qry_history()[1])
    assert compare_query(update_mam_qry(3, 'mam_doc3.xml'),
                         update_conn.qry_history()[2])
    assert compare_query(update_mam_qry(4, 'mam_doc4.xml'),
                         update_conn.qry_history()[3])
    assert compare_query(update_mam_qry(5, 'mam_doc5.xml'),
                         update_conn.qry_history()[4])

    assert read_conn.close_count == 1
    assert update_conn.close_count == 1
