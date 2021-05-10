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
            "create_harvest_table": ["harvest_vkc"],
            "harvest_vkc": ["transform_xml"],
            "transform_xml": ["push_to_rabbitmq"],
            "push_to_rabbitmq": []
        }, dag)
