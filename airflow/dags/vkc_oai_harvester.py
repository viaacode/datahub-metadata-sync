"""Example DAG demonstrating the usage of the PythonOperator."""
import time
from pprint import pprint

from airflow import DAG
from airflow.operators.python import PythonOperator, PythonVirtualenvOperator
from airflow.utils.dates import days_ago
from task_services.oai_api import OaiApi

args = {
    'owner': 'airflow',
}

dag = DAG(
    dag_id='vkc_oai_harvester',
    default_args=args,
    schedule_interval=None,
    start_date=days_ago(2),
    tags=['VKC'],
)


def harvest_oai(full_sync=False):
    print(f'harvest_oai called with full_sync={full_sync} harvest OAI data and store it in database')
    oai_api = OaiApi()
    results = oai_api.get_data()
    time.sleep(2)
    return results

def transform_lido_to_mh(**context):
    print(f'transform_lido_to_mh called with context={context} transform xml format by iterating database')
    time.sleep(1)

def publish_to_rabbitmq(**context):
    print(f'publish_to_rabbitmq called with context={context} pushes data to rabbit mq')
    time.sleep(3)


with dag:
    harvest_oai_task = PythonOperator(
        task_id='harvest_oai',
        python_callable=harvest_oai,
        op_kwargs={'full_sync': True}
    )

    transform_lido_task = PythonOperator(
        task_id='transform_lido_to_mh',
        python_callable=transform_lido_to_mh,
    )

    publish_to_rabbitmq_task = PythonOperator(
        task_id='publish_to_rabbitmq',
        python_callable=publish_to_rabbitmq,
    )

    harvest_oai_task >> transform_lido_task >> publish_to_rabbitmq_task


# Example of virtualenv python, right now we don't need it as we just incorporated
# wanted packages in the main env usign requirements.txt
# # [START howto_operator_python_venv]
# def callable_virtualenv():
#     """
#     Example function that will be performed in a virtual environment.
# 
#     Importing at the module level ensures that it will not attempt to import the
#     library before it is installed.
#     """
#     from time import sleep
# 
#     from colorama import Back, Fore, Style
# 
#     print(Fore.RED + 'some red text')
#     print(Back.GREEN + 'and with a green background')
#     print(Style.DIM + 'and in dim text')
#     print(Style.RESET_ALL)
#     for _ in range(10):
#         print(Style.DIM + 'Please wait...', flush=True)
#         sleep(3)
#     print('Finished')
# 
# 
# virtualenv_task = PythonVirtualenvOperator(
#     task_id="virtualenv_python",
#     python_callable=callable_virtualenv,
#     requirements=["colorama==0.4.0"],
#     system_site_packages=False,
#     dag=dag,
# )
# # [END howto_operator_python_venv]
