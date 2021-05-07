# datahub-metadata-sync
Synchronisatie van metadata tussen meemoo en de datahub van VKC.


# Installation

A makefile is in progress that will replace most of the following scripts, just execute make and see available tasks.

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
[2021-04-27 19:22:11,352] {dagbag.py:451} INFO - Filling up the DagBag from /Users/wschrep/FreelanceWork/VIAA/IIIF_newproject/datahub-metadata-sync/airflow/dags
[2021-04-27 19:22:11,381] {taskinstance.py:877} INFO - Dependencies all met for <TaskInstance: vkc_oai_harvester.harvest_oai 2015-06-01T00:00:00+00:00 [None]>
[2021-04-27 19:22:11,390] {taskinstance.py:877} INFO - Dependencies all met for <TaskInstance: vkc_oai_harvester.harvest_oai 2015-06-01T00:00:00+00:00 [None]>
[2021-04-27 19:22:11,390] {taskinstance.py:1068} INFO - 
--------------------------------------------------------------------------------
[2021-04-27 19:22:11,390] {taskinstance.py:1069} INFO - Starting attempt 1 of 1
[2021-04-27 19:22:11,391] {taskinstance.py:1070} INFO - 
--------------------------------------------------------------------------------
[2021-04-27 19:22:11,393] {taskinstance.py:1089} INFO - Executing <Task(PythonOperator): harvest_oai> on 2015-06-01T00:00:00+00:00
[2021-04-27 19:22:11,479] {taskinstance.py:1281} INFO - Exporting the following env vars:
AIRFLOW_CTX_DAG_OWNER=airflow
AIRFLOW_CTX_DAG_ID=vkc_oai_harvester
AIRFLOW_CTX_TASK_ID=harvest_oai
AIRFLOW_CTX_EXECUTION_DATE=2015-06-01T00:00:00+00:00
harvest_oai called with full_sync=True harvest OAI data and store it in database
[2021-04-27 19:22:11,489] {base.py:69} INFO - Using connection to: id: postgres_default. Host: localhost, Port: 5432, Schema: airflow_development, Login: postgres, Password: XXXXXXXX, extra: None
OaiApi initialized
Saving 100 of 15901 records progress is 0.6 %
Saving 100 of 15901 records progress is 1.2 %
Saving 100 of 15901 records progress is 1.8 %
Saving 100 of 15901 records progress is 2.5 %
Saving 100 of 15901 records progress is 3.1 %
Saving 100 of 15901 records progress is 3.7 %
Saving 100 of 15901 records progress is 4.4 %

...
Saving 100 of 15901 records progress is 91.8 %
Saving 100 of 15901 records progress is 92.4 %
Saving 100 of 15901 records progress is 93.0 %
Saving 100 of 15901 records progress is 93.7 %
Saving 100 of 15901 records progress is 94.3 %
Saving 100 of 15901 records progress is 94.9 %
Saving 100 of 15901 records progress is 95.5 %
Saving 100 of 15901 records progress is 96.2 %
Saving 100 of 15901 records progress is 96.8 %
Saving 100 of 15901 records progress is 97.4 %
Saving 100 of 15901 records progress is 98.1 %
Saving 100 of 15901 records progress is 98.7 %
Saving 100 of 15901 records progress is 99.3 %
Saving 100 of 15901 records progress is 99.9 %
Saving 1 of 15901 records progress is 100.0 %
[2021-04-27 19:24:31,314] {python.py:118} INFO - Done. Returned value was: None
[2021-04-27 19:24:31,320] {taskinstance.py:1185} INFO - Marking task as SUCCESS. dag_id=vkc_oai_harvester, task_id=harvest_oai, execution_date=20150601T000000, start_date=20210427T172211, end_date=20210427T172431
```


Testrun a transformation after a harvest run.
This shows we can do batch sized queries (configured with BATCH_SIZE at top of DAG file) and then update these batches in a single commit per batch.
We use a second connection and a named cursor on the read connection to make this all work nicely.

```
airflow tasks test vkc_oai_harvester transform_lido_to_mh 2015-06-01

[2021-04-27 14:31:09,757] {dagbag.py:451} INFO - Filling up the DagBag from /Users/wschrep/FreelanceWork/VIAA/IIIF_newproject/datahub-metadata-sync/airflow/dags
[2021-04-27 14:31:09,796] {taskinstance.py:877} INFO - Dependencies all met for <TaskInstance: vkc_oai_harvester.transform_lido_to_mh 2015-06-01T00:00:00+00:00 [None]>
[2021-04-27 14:31:09,808] {taskinstance.py:877} INFO - Dependencies all met for <TaskInstance: vkc_oai_harvester.transform_lido_to_mh 2015-06-01T00:00:00+00:00 [None]>
[2021-04-27 14:31:09,808] {taskinstance.py:1068} INFO -
--------------------------------------------------------------------------------
[2021-04-27 14:31:09,808] {taskinstance.py:1069} INFO - Starting attempt 1 of 1
[2021-04-27 14:31:09,808] {taskinstance.py:1070} INFO -
--------------------------------------------------------------------------------
[2021-04-27 14:31:09,809] {taskinstance.py:1089} INFO - Executing <Task(PythonOperator): transform_lido_to_mh> on 2015-06-01T00:00:00+00:00
[2021-04-27 14:31:09,900] {taskinstance.py:1281} INFO - Exporting the following env vars:
AIRFLOW_CTX_DAG_OWNER=airflow
AIRFLOW_CTX_DAG_ID=vkc_oai_harvester
AIRFLOW_CTX_TASK_ID=transform_lido_to_mh
AIRFLOW_CTX_EXECUTION_DATE=2015-06-01T00:00:00+00:00
transform_lido_to_mh called with context={'conf': ...} transform xml format by iterating database
XmlTransformer initialized
[2021-04-27 14:31:09,905] {base.py:69} INFO - Using connection to: id: postgres_default. Host: localhost, Port: 5432, Schema: airflow_development, Login: postgres, Password: XXXXXXXX, extra: None
[2021-04-27 14:31:09,916] {base.py:69} INFO - Using connection to: id: postgres_default. Host: localhost, Port: 5432, Schema: airflow_development, Login: postgres, Password: XXXXXXXX, extra: None
fetched 2 records, now converting...
updating record id=4 mam_data=TODO CONVERT TO MAM FORMAT:some result xml document from OAI
updating record id=2 mam_data=TODO CONVERT TO MAM FORMAT:some result xml document from OAI
fetched 2 records, now converting...
updating record id=3 mam_data=TODO CONVERT TO MAM FORMAT:some result xml document from OAI
updating record id=5 mam_data=TODO CONVERT TO MAM FORMAT:some result xml document from OAI
[2021-04-27 14:31:09,932] {python.py:118} INFO - Done. Returned value was: None
[2021-04-27 14:31:09,938] {taskinstance.py:1185} INFO - Marking task as SUCCESS. dag_id=vkc_oai_harvester, task_id=transform_lido_to_mh, execution_date=20150601T000000, start_date=20210427T123109, end_date=20210427T123109
```



# Testing
Using the makefile you can generate a test coverage report

```
$ make coverage
================================= test session starts =================================
platform darwin -- Python 3.8.5, pytest-5.3.5, py-1.10.0, pluggy-0.13.1
rootdir: /Users/wschrep/FreelanceWork/VIAA/IIIF_newproject/datahub-metadata-sync
plugins: cov-2.8.1, mock-3.5.1
collected 2 items

tests/test_dag_tasks.py .                                                       [ 50%]
tests/test_harvest_dag.py .                                                     [100%]

---------- coverage: platform darwin, python 3.8.5-final-0 -----------
Name                                             Stmts   Miss  Cover
--------------------------------------------------------------------
airflow/dags/task_services/__init__.py               0      0   100%
airflow/dags/task_services/harvest_table.py         30     12    60%
airflow/dags/task_services/mediahaven_api.py        34     23    32%
airflow/dags/task_services/rabbit.py                40     33    18%
airflow/dags/task_services/rabbit_publisher.py      11      6    45%
airflow/dags/task_services/vkc_api.py               41     36    12%
airflow/dags/task_services/xml_transformer.py       17     10    41%
airflow/dags/vkc_oai_harvester.py                   92     68    26%
--------------------------------------------------------------------
TOTAL                                              265    188    29%
Coverage HTML written to dir htmlcov


================================== 2 passed in 1.58s ==================================
```
In next days we will be improving testing coverage.


