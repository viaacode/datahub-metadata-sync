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

```
airflow tasks test vkc_oai_harvester  virtualenv_python 2015-06-01
```
