# datahub-metadata-sync
Synchronisatie van metadata tussen meemoo en de datahub van VKC.


# Installation

Just run make install to install python virtual env and install the packages
in requirements.txt:
```
$ make install
```

Migrate the initial database only needs to be done once and uses following script:

Then migrate/create the database tables using:
```
$ scripts/migrate_database.sh
```
Here you also need to enter an admin user and password (keep these as you need them later to
login when starting the webserver with the airflow interface)



# Running the server and scheduler

A makefile is provided and when you run make without arguments you see the available commands:
```
$ make
Available make commands:

  install     install packages and prepare environment
  clean       remove all temporary files
  lint        run the code linters
  format      reformat code
  test        run all the tests
  dockertest  run all the tests in docker image like jenkins
  coverage    run tests and generate coverage report
  server      start airflow webserver port 8080
  scheduler   start airflow scheculer to run dags
```


Start the scheduler like so:
```
$ make scheduler
```

And in seperate window start the webserver:
```
$ make server
```

Now just open a browser window to http://localhost:8080 to see the airflow interface.
There is only one dag defined/available and you can run it from there.



# VKC OAI Harvester
This is defined in airflow/dags
Before trying out below commands, have these exports in place:
```
export AIRFLOW_HOME=$(PWD)/airflow
export AIRFLOW__CORE__SQL_ALCHEMY_CONN=postgresql+psycopg2://postgres:postgres@localhost:5432/airflow_development
```



Listing the tasks in this harvester:
```
$ airflow tasks list vkc_oai_harvester

[2021-05-25 12:08:23,255] {dagbag.py:451} INFO - Filling up the DagBag from /Users/wschrep/FreelanceWork/VIAA/IIIF_newproject/datahub-metadata-sync/airflow/dags
create_harvest_table
create_mapping_table
harvest_mapping
harvest_vkc
push_to_rabbitmq
transform_xml
```

Run task to create the harvest table:
```
$ airflow tasks test vkc_oai_harvester create_harvest_table 2021-05-08
```

Run task to create the work_id mapping table:
```
$ airflow tasks test vkc_oai_harvester create_mapping_table 2021-05-08
```


First populate the mapping table, this maps work_id's to the fragment_ids and is used in later tasks by joining the
harvest_vkc table on mapping_vkc by matching work_id.
Once the table is populated it won't do a full run unless the number of results of the mam qry changes.
(unless when passing in full_sync=True, then this is done always and the old mapping is truncated)

```
$ airflow tasks test vkc_oai_harvester harvest_mapping 2015-06-01

...
Found 32743 inventarisnummers.
Using existing mapping table mapping_vkc.
```



Testrun a task for instance harvest oai data to target database, for first call even delta does full_sync as table is empty:
```
$ airflow tasks test vkc_oai_harvester harvest_vkc 2015-06-01

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


Run the xml transformation after a harvest run. This transforms all the vkc lido xml blobs into mediahaven compatible xml. It is stored in the column
mam_xml along with a call to mediahaven to get the fragment_id, cp_id based on the work_id saved in previous harvest job.


To run a delta task, just pass full_sync is false as an argument example from cli (or omit it as this does delta also now):
```
$ airflow tasks test vkc_oai_harvester harvest_vkc 2015-06-01 -t '{"full_sync": false}'
```

To execute a full_sync we can pass this as follows :
```
$ airflow tasks test vkc_oai_harvester harvest_vkc 2015-06-01 -t '{"full_sync": true}'
```
This truncates the table, then does full sync.




```
$ airflow tasks test vkc_oai_harvester transform_xml 2015-06-01

[2021-05-08 17:32:07,767] {dagbag.py:451} INFO - Filling up the DagBag from /Users/wschrep/FreelanceWork/VIAA/IIIF_newproject/datahub-metadata-sync/airflow/dags
[2021-05-08 17:32:07,832] {taskinstance.py:877} INFO - Dependencies all met for <TaskInstance: vkc_oai_harvester.transform_xml 2015-06-01T00:00:00+00:00 [None]>
[2021-05-08 17:32:07,840] {taskinstance.py:877} INFO - Dependencies all met for <TaskInstance: vkc_oai_harvester.transform_xml 2015-06-01T00:00:00+00:00 [None]>
[2021-05-08 17:32:07,840] {taskinstance.py:1068} INFO -
--------------------------------------------------------------------------------
[2021-05-08 17:32:07,840] {taskinstance.py:1069} INFO - Starting attempt 1 of 1
[2021-05-08 17:32:07,841] {taskinstance.py:1070} INFO -
--------------------------------------------------------------------------------
[2021-05-08 17:32:07,841] {taskinstance.py:1089} INFO - Executing <Task(PythonOperator): transform_xml> on 2015-06-01T00:00:00+00:00
[2021-05-08 17:32:07,919] {taskinstance.py:1281} INFO - Exporting the following env vars:
AIRFLOW_CTX_DAG_OWNER=airflow
AIRFLOW_CTX_DAG_ID=vkc_oai_harvester
AIRFLOW_CTX_TASK_ID=transform_xml
AIRFLOW_CTX_EXECUTION_DATE=2015-06-01T00:00:00+00:00
transform_lido_to_mh called, ... 
XmlTransformer initialized
[2021-05-08 17:32:08,126] {base.py:69} INFO - Using connection to: id: postgres_default. Host: localhost, Port: 5432, Schema: airflow_development, Login: postgres, Password: XXXXXXXX, extra: None
[2021-05-08 17:32:08,136] {base.py:69} INFO - Using connection to: id: postgres_default. Host: localhost, Port: 5432, Schema: airflow_development, Login: postgres, Password: XXXXXXXX, extra: None
fetched 100 records, now converting...
Skipping record with work_id=0000.GRO1561.I
Skipping record with work_id=0000.GRO1390.I
Skipping record with work_id=0000.GRO0128.I
Skipping record with work_id=0000.GRO1476.I
Skipping record with work_id=0000.GRO0479.I
Skipping record with work_id=0000.GRO1372.I
Skipping record with work_id=0000.GRO1360.I
Skipping record with work_id=0000.GRO1359.I
Skipping record with work_id=0000.GRO0227.I
Record work_id=0000.GRO1280.I found, fragment_id=7ba7f34a1d3b404590d7bcaa7f93687ce6e986214b8442cfb168d9fcf85b9194686ad969521f415c8a1bbbca34919135 cp_id=OR-x921j0n
Skipping record with work_id=0000.GRO1243.I
Skipping record with work_id=0000.GRO0299.I
...

```
So when a record is found in mediahaven using the api then we convert the xml and fill in the fragment_id and cp_id needed for the last task, sending it with rabbitmq as
a mam-update-request.



To now send the records to be updated with a task we run the following (the date is not really used, instead we look at the synchronized boolean flag, all that are not set to true will be sent and then the flag is updated to true):

To test a few records, just run this query:
update harvest_vkc set synchronized=true;
and then manually set a few records to synchronized=false and then run the publis_to_rabbitmq task so it sends the ones where the flag is false.

```
$ airflow tasks test vkc_oai_harvester push_to_rabbitmq 2021-05-01
...
```



# Testing
Using the makefile you can generate a test coverage report
This uses sqlite3 for running the tests so we don't destroy any valuable data and also this is easier
to integrate in our openshift tests. We use the dbfile airflow/airflow.db sqlite database in the first
2 dag tests and for the other actual task code we test using a custom written mock_database class which is
in tests/mock_database.py. 

```
$ make coverage
DB: sqlite:////Users/wschrep/FreelanceWork/VIAA/IIIF_newproject/datahub-metadata-sync/airflow/airflow.db
[2021-06-10 10:20:38,315] {db.py:684} INFO - Creating tables
INFO  [alembic.runtime.migration] Context impl SQLiteImpl.
INFO  [alembic.runtime.migration] Will assume non-transactional DDL.
WARNI [airflow.models.crypto] empty cryptography key - values will not be stored encrypted.
Initialization done
====================================== test session starts ======================================
platform darwin -- Python 3.9.5, pytest-6.2.4, py-1.10.0, pluggy-0.13.1
rootdir: /Users/wschrep/FreelanceWork/VIAA/IIIF_newproject/datahub-metadata-sync
plugins: recording-0.11.0, docker-tools-1.0.3, cov-2.8.1, mock-3.5.1
collected 9 items                                                                               

tests/test_dag_tasks.py .                                                                 [ 11%]
tests/test_harvest_dag.py .                                                               [ 22%]
tests/test_harvest_mapping_job.py ..                                                      [ 44%]
tests/test_harvest_vkc_job.py ..                                                          [ 66%]
tests/test_pg_conn_mock.py .                                                              [ 77%]
tests/test_publish_updates_job.py .                                                       [ 88%]
tests/test_transform_xml_job.py .                                                         [100%]

---------- coverage: platform darwin, python 3.9.5-final-0 -----------
Name                                                Stmts   Miss  Cover
-----------------------------------------------------------------------
airflow/dags/task_services/__init__.py                  0      0   100%
airflow/dags/task_services/harvest_mapping_job.py      29      0   100%
airflow/dags/task_services/harvest_table.py            54      1    98%
airflow/dags/task_services/harvest_vkc_job.py          27      2    93%
airflow/dags/task_services/mapping_table.py            30      1    97%
airflow/dags/task_services/mediahaven_api.py           24      1    96%
airflow/dags/task_services/publish_updates_job.py      27      0   100%
airflow/dags/task_services/rabbit.py                   46     37    20%
airflow/dags/task_services/transform_xml_job.py        29      0   100%
airflow/dags/task_services/transformer_process.py      19      0   100%
airflow/dags/task_services/vkc_api.py                  78     10    87%
airflow/dags/task_services/xml_transformer.py          17      0   100%
airflow/dags/vkc_oai_harvester.py                      42     16    62%
-----------------------------------------------------------------------
TOTAL                                                 422     68    84%
Coverage HTML written to dir htmlcov


======================================= 9 passed in 3.47s =======================================
```

The VkcApi and MediahavenApi data are now mocked using pytest-recorder (responses are saved as yaml files in the tests).
The harvest_mapping and harvest_vkc are well enough tested. The xml transformer is work in progress but is already
running some tests. 



# Docker container build

Build a container with saxonc for xml transformer and complete airflow installation.

```
$ scripts/docker_build.sh
```


Run webserver and scheduler inside docker container:
```
$ scripts/docker_run.sh
```


For debugging the container, theres a helper login script:
```
$ scripts/docker_login.sh
```


# Mocking/testing airflow

This seems quite challenging. I got quickly to a point where we can call tasks from within our tests. But mocking the database and api calls
seems a bit harder inside the airflow tests. Problem is we're not directly calling a method but using .execute. Mocking in this case is
harder to do. We might need to refactor some more stuff in order to be able to automate testing code.

Right now if the database and api calls are available the tests do a full sync and this takes a long time it does however result in 70% code coverage.
However we need to mock it to make tests run faster and more reliably.

Current research/links we have found regarding testing airflow tasks:

* https://airflowsummit.org/slides/j2-Ensuring-your-DAGs-work-before-going-to-production.pdf
* https://godatadriven.com/blog/testing-and-debugging-apache-airflow/
* https://medium.com/wbaa/datas-inferno-7-circles-of-data-testing-hell-with-airflow-cef4adff58d8
* https://airflow.apache.org/docs/apache-airflow/stable/best-practices.html

However up to now we need some further trial/error to get something that works nicely in our setup.

