#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  @Author: Walter Schreppers
#
#  tests/test_dag_tasks.py
#
#   This tests our dag file and validates the structure
#   of the various tasks, create_mapping, harvest_vkc etc.
#   It works on a sqlite database that is created+migrated in the makefile
#   when you run 'make test'
#

import unittest
from airflow.models import DagBag


class testClass(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.dagbag = DagBag()

    def assertDagDictEqual(self, source, dag):
        assert dag.task_dict.keys() == source.keys()
        for task_id, downstream_list in source.items():
            assert dag.has_task(task_id)
            task = dag.get_task(task_id)
            assert task.downstream_task_ids == set(downstream_list)

    def test_dag_task_order(self):
        dag = self.dagbag.get_dag(dag_id='vkc_oai_harvester')

        self.assertDagDictEqual({
            "create_harvest_table": ["create_mapping_table"],
            "create_mapping_table": ["harvest_vkc"],
            "harvest_vkc": ["harvest_mapping"],
            "harvest_mapping": ["transform_xml"],
            "transform_xml": ["push_to_rabbitmq"],
            "push_to_rabbitmq": []
        }, dag)
