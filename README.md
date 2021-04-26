# datahub-metadata-sync
Synchronisatie van metadata tussen meemoo en de datahub van VKC.


# Installation

Install pip packages and create python virtual env
```
scripts/install_airflow.sh
```

Then migrate/create the database tables using:
```
scripts/migrate_database.sh
```

Finally start the scheduler like so:
```
scripts/start_schedular.sh
```

And in seperate window start the webserver:
```
scripts/start_webserver.sh
```

... (todo need to add pip install apache-airflow['cncf.kubernetes'] or fix config so we dont have warnings about missing this package)


# VKC OAI Harvester
This is defined in airflow/dags
Before trying out below commands, have these exports in place:
```
export AIRFLOW_HOME=$(PWD)/airflow
export AIRFLOW__CORE__SQL_ALCHEMY_CON=postgresql+psycopg2://postgres:postgres@localhost:5432/airflow_development
```



Listing the tasks in this harvester:

```
airflow tasks list vkc_oai_harvester

[2021-04-26 16:32:34,415] {dagbag.py:451} INFO - Filling up the DagBag from .../airflow/dags
harvest_oai
publish_to_rabbitmq
transform_lido_to_mh

```

Testrun a task for instance harvest oai data to target database:

```
airflow tasks test vkc_oai_harvester  harvest_oai 2015-06-01
[2021-04-26 16:34:39,043] {dagbag.py:451} INFO - Filling up the DagBag from /Users/wschrep/FreelanceWork/VIAA/IIIF_newproject/datahub-metadata-sync/airflow/dags
[2021-04-26 16:34:39,064] {taskinstance.py:877} INFO - Dependencies all met for <TaskInstance: vkc_oai_harvester.harvest_oai 2015-06-01T00:00:00+00:00 [None]>
[2021-04-26 16:34:39,071] {taskinstance.py:877} INFO - Dependencies all met for <TaskInstance: vkc_oai_harvester.harvest_oai 2015-06-01T00:00:00+00:00 [None]>
[2021-04-26 16:34:39,071] {taskinstance.py:1068} INFO -
--------------------------------------------------------------------------------
[2021-04-26 16:34:39,071] {taskinstance.py:1069} INFO - Starting attempt 1 of 1
[2021-04-26 16:34:39,071] {taskinstance.py:1070} INFO -
--------------------------------------------------------------------------------
[2021-04-26 16:34:39,072] {taskinstance.py:1089} INFO - Executing <Task(PythonOperator): harvest_oai> on 2015-06-01T00:00:00+00:00
[2021-04-26 16:34:39,147] {taskinstance.py:1281} INFO - Exporting the following env vars:
AIRFLOW_CTX_DAG_OWNER=airflow
AIRFLOW_CTX_DAG_ID=vkc_oai_harvester
AIRFLOW_CTX_TASK_ID=harvest_oai
AIRFLOW_CTX_EXECUTION_DATE=2015-06-01T00:00:00+00:00
harvest_oai called with context={'conf': <airflow.configuration.AirflowConfigParser object at 0x10d0ab3d0>, 'dag': <DAG: vkc_oai_harvester>, 'dag_run': None, 'ds': '2015-06-01', 'ds_nodash': '20150601', 'execution_date': DateTime(2015, 6, 1, 0, 0, 0, tzinfo=Timezone('UTC')), 'inlets': [], 'macros': <module 'airflow.macros' from '/Users/wschrep/FreelanceWork/VIAA/IIIF_newproject/datahub-metadata-sync/python_env/lib/python3.8/site-packages/airflow/macros/__init__.py'>, 'next_ds': None, 'next_ds_nodash': None, 'next_execution_date': None, 'outlets': [], 'params': {}, 'prev_ds': None, 'prev_ds_nodash': None, 'prev_execution_date': None, 'prev_execution_date_success': <Proxy at 0x10ee0bd00 with factory <function TaskInstance.get_template_context.<locals>.<lambda> at 0x10edd78b0>>, 'prev_start_date_success': <Proxy at 0x10ee0b4c0 with factory <function TaskInstance.get_template_context.<locals>.<lambda> at 0x10edf0ee0>>, 'run_id': None, 'task': <Task(PythonOperator): harvest_oai>, 'task_instance': <TaskInstance: vkc_oai_harvester.harvest_oai 2015-06-01T00:00:00+00:00 [None]>, 'task_instance_key_str': 'vkc_oai_harvester__harvest_oai__20150601', 'test_mode': True, 'ti': <TaskInstance: vkc_oai_harvester.harvest_oai 2015-06-01T00:00:00+00:00 [None]>, 'tomorrow_ds': '2015-06-02', 'tomorrow_ds_nodash': '20150602', 'ts': '2015-06-01T00:00:00+00:00', 'ts_nodash': '20150601T000000', 'ts_nodash_with_tz': '20150601T000000+0000', 'var': {'json': None, 'value': None}, 'yesterday_ds': '2015-05-31', 'yesterday_ds_nodash': '20150531', 'templates_dict': None} harvest OAI data and store it in database
OaiApi initialized
[2021-04-26 16:34:41,152] {python.py:118} INFO - Done. Returned value was: []
[2021-04-26 16:34:41,164] {taskinstance.py:1185} INFO - Marking task as SUCCESS. dag_id=vkc_oai_harvester, task_id=harvest_oai, execution_date=20150601T000000, start_date=20210426T143439, end_date=20210426T143441

```


