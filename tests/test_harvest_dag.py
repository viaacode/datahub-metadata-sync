#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  @Author: Walter Schreppers
#
#  tests/test_dag_tasks.py
#
#   This tests our dag file for the dag vkc_oai_harvester
#   it basically is a check that no import errors or other
#   compile errors are found. It does not however fully start
#   a dag (as this is done more granulary in the test_..._job.py's
#   where we need to mock the database connection and use recorded
#   pytest-recorder responses
#

from airflow.models import DagBag
import unittest


class TestHarvestDAG(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dagbag = DagBag()

    def test_dag_loaded(self):
        dag = self.dagbag.get_dag(dag_id='vkc_oai_harvester')
        assert self.dagbag.import_errors == {}
        assert dag is not None
        assert len(dag.tasks) == 6
