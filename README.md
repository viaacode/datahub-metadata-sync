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
[2021-04-23 14:54:32,998] {dagbag.py:451} INFO - Filling up the DagBag from /Users/wschrep/FreelanceWork/VIAA/IIIF_newproject/datahub-metadata-sync/airflow/dags
[2021-04-23 14:54:33,062] {example_kubernetes_executor_config.py:175} WARNING - Could not import DAGs in example_kubernetes_executor_config.py: No module named 'kubernetes'
[2021-04-23 14:54:33,063] {example_kubernetes_executor_config.py:176} WARNING - Install kubernetes dependencies with: pip install apache-airflow['cncf.kubernetes']
print_the_context
sleep_for_0
sleep_for_1
sleep_for_2
sleep_for_3
sleep_for_4
virtualenv_python
```

Testrun a task:

```
airflow tasks test vkc_oai_harvester  print_the_context 2015-06-01
```



This runs a longer task with a python virtual_env. It sleeps some seconds and prints out a message.
Tasks runs ok now:

```
airflow tasks test vkc_oai_harvester  virtualenv_python 2015-06-01

[2021-04-23 15:04:16,394] {dagbag.py:451} INFO - Filling up the DagBag from /Users/wschrep/FreelanceWork/VIAA/IIIF_newproject/datahub-metadata-sync/airflow/dags
[2021-04-23 15:04:16,464] {baseoperator.py:1186} WARNING - Dependency <Task(BashOperator): create_entry_group>, delete_entry_group already registered
[2021-04-23 15:04:16,464] {baseoperator.py:1186} WARNING - Dependency <Task(BashOperator): delete_entry_group>, create_entry_group already registered
[2021-04-23 15:04:16,465] {baseoperator.py:1186} WARNING - Dependency <Task(BashOperator): create_entry_gcs>, delete_entry already registered
[2021-04-23 15:04:16,465] {baseoperator.py:1186} WARNING - Dependency <Task(BashOperator): delete_entry>, create_entry_gcs already registered
[2021-04-23 15:04:16,465] {baseoperator.py:1186} WARNING - Dependency <Task(BashOperator): create_tag>, delete_tag already registered
[2021-04-23 15:04:16,465] {baseoperator.py:1186} WARNING - Dependency <Task(BashOperator): delete_tag>, create_tag already registered
[2021-04-23 15:04:16,486] {example_kubernetes_executor_config.py:175} WARNING - Could not import DAGs in example_kubernetes_executor_config.py: No module named 'kubernetes'
[2021-04-23 15:04:16,486] {example_kubernetes_executor_config.py:176} WARNING - Install kubernetes dependencies with: pip install apache-airflow['cncf.kubernetes']
[2021-04-23 15:04:16,492] {baseoperator.py:1186} WARNING - Dependency <Task(_PythonDecoratedOperator): prepare_email>, send_email already registered
[2021-04-23 15:04:16,492] {baseoperator.py:1186} WARNING - Dependency <Task(EmailOperator): send_email>, prepare_email already registered
[2021-04-23 15:04:16,533] {taskinstance.py:877} INFO - Dependencies all met for <TaskInstance: vkc_oai_harvester.virtualenv_python 2015-06-01T00:00:00+00:00 [None]>
[2021-04-23 15:04:16,539] {taskinstance.py:877} INFO - Dependencies all met for <TaskInstance: vkc_oai_harvester.virtualenv_python 2015-06-01T00:00:00+00:00 [None]>
[2021-04-23 15:04:16,539] {taskinstance.py:1068} INFO -
--------------------------------------------------------------------------------
[2021-04-23 15:04:16,539] {taskinstance.py:1069} INFO - Starting attempt 1 of 1
[2021-04-23 15:04:16,539] {taskinstance.py:1070} INFO -
--------------------------------------------------------------------------------
[2021-04-23 15:04:16,540] {taskinstance.py:1089} INFO - Executing <Task(PythonVirtualenvOperator): virtualenv_python> on 2015-06-01T00:00:00+00:00
[2021-04-23 15:04:42,815] {taskinstance.py:1281} INFO - Exporting the following env vars:
AIRFLOW_CTX_DAG_OWNER=airflow
AIRFLOW_CTX_DAG_ID=vkc_oai_harvester
AIRFLOW_CTX_TASK_ID=virtualenv_python
AIRFLOW_CTX_EXECUTION_DATE=2015-06-01T00:00:00+00:00
[2021-04-23 15:04:42,816] {process_utils.py:135} INFO - Executing cmd: virtualenv /var/folders/68/c_pd8_vj55d9mdvv3mvllkh00000gn/T/venv2qgown6q
[2021-04-23 15:04:42,822] {process_utils.py:137} INFO - Output:
[2021-04-23 15:04:43,767] {process_utils.py:141} INFO - created virtual environment CPython3.8.5.final.0-64 in 583ms
[2021-04-23 15:04:43,767] {process_utils.py:141} INFO -   creator CPython3Posix(dest=/private/var/folders/68/c_pd8_vj55d9mdvv3mvllkh00000gn/T/venv2qgown6q, clear=False, no_vcs_ignore=False, global=False)
[2021-04-23 15:04:43,768] {process_utils.py:141} INFO -   seeder FromAppData(download=False, pip=bundle, setuptools=bundle, wheel=bundle, via=copy, app_data_dir=/Users/wschrep/Library/Application Support/virtualenv)
[2021-04-23 15:04:43,768] {process_utils.py:141} INFO -     added seed packages: pip==21.0.1, setuptools==52.0.0, wheel==0.36.2
[2021-04-23 15:04:43,768] {process_utils.py:141} INFO -   activators BashActivator,CShellActivator,FishActivator,PowerShellActivator,PythonActivator,XonshActivator
[2021-04-23 15:04:43,792] {process_utils.py:135} INFO - Executing cmd: /var/folders/68/c_pd8_vj55d9mdvv3mvllkh00000gn/T/venv2qgown6q/bin/pip install colorama==0.4.0
[2021-04-23 15:04:43,795] {process_utils.py:137} INFO - Output:
[2021-04-23 15:04:44,996] {process_utils.py:141} INFO - Looking in indexes: http://do-prd-mvn-01.do.viaa.be:8081/repository/pypi-all/simple
[2021-04-23 15:04:45,178] {process_utils.py:141} INFO - Collecting colorama==0.4.0
[2021-04-23 15:04:45,643] {process_utils.py:141} INFO -   Downloading http://do-prd-mvn-01.do.viaa.be:8081/repository/pypi-all/packages/0a/93/6e8289231675d561d476d656c2ee3a868c1cca207e16c118d4503b25e2bf/colorama-0.4.0-py2.py3-none-any.whl (21 kB)
[2021-04-23 15:04:45,706] {process_utils.py:141} INFO - Installing collected packages: colorama
[2021-04-23 15:04:45,732] {process_utils.py:141} INFO - Successfully installed colorama-0.4.0
[2021-04-23 15:04:46,285] {process_utils.py:135} INFO - Executing cmd: /var/folders/68/c_pd8_vj55d9mdvv3mvllkh00000gn/T/venv2qgown6q/bin/python /var/folders/68/c_pd8_vj55d9mdvv3mvllkh00000gn/T/venv2qgown6q/script.py /var/folders/68/c_pd8_vj55d9mdvv3mvllkh00000gn/T/venv2qgown6q/script.in /var/folders/68/c_pd8_vj55d9mdvv3mvllkh00000gn/T/venv2qgown6q/script.out /var/folders/68/c_pd8_vj55d9mdvv3mvllkh00000gn/T/venv2qgown6q/string_args.txt
[2021-04-23 15:04:46,288] {process_utils.py:137} INFO - Output:
[2021-04-23 15:04:46,329] {process_utils.py:141} INFO - some red text
[2021-04-23 15:04:46,329] {process_utils.py:141} INFO - and with a green background
[2021-04-23 15:04:46,330] {process_utils.py:141} INFO - and in dim text
[2021-04-23 15:04:46,330] {process_utils.py:141} INFO -
[2021-04-23 15:04:46,330] {process_utils.py:141} INFO - Please wait...
[2021-04-23 15:04:56,332] {process_utils.py:141} INFO - Please wait...
[2021-04-23 15:05:06,332] {process_utils.py:141} INFO - Please wait...
[2021-04-23 15:05:16,338] {process_utils.py:141} INFO - Please wait...
[2021-04-23 15:05:26,343] {process_utils.py:141} INFO - Please wait...
[2021-04-23 15:05:36,348] {process_utils.py:141} INFO - Please wait...
[2021-04-23 15:06:16,359] {process_utils.py:141} INFO - Please wait...
[2021-04-23 15:06:26,362] {process_utils.py:141} INFO - Finished
[2021-04-23 15:06:26,552] {python.py:118} INFO - Done. Returned value was: None
[2021-04-23 15:06:26,561] {taskinstance.py:1185} INFO - Marking task as SUCCESS. dag_id=vkc_oai_harvester, task_id=virtualenv_python, execution_date=20150601T000000, start_date=20210423T130416, end_date=20210423T130626

```
