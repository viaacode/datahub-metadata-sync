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
harvest_oai called with context={'conf': ... harvest OAI data and store it in database
OaiApi initialized
[2021-04-26 16:34:41,152] {python.py:118} INFO - Done. Returned value was: []
[2021-04-26 16:34:41,164] {taskinstance.py:1185} INFO - Marking task as SUCCESS. dag_id=vkc_oai_harvester, task_id=harvest_oai, execution_date=20150601T000000, start_date=20210426T143439, end_date=20210426T143441

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

