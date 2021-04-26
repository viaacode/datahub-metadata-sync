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


def harvest_oai(**context):
    print(f'harvest_oai called with context={context} harvest OAI data and store it in database')
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
        # provide_context=True
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



# original example code, does a lot of things we currently don't need yet but keeping
# this for later inspiration. 
# TODO clear this out once above dag is finished:

# # [START howto_operator_python]
# def print_context(ds, **kwargs):
#     """Print the Airflow context and ds variable from the context."""
#     pprint(kwargs)
#     print(ds)
#     return 'Whatever you return gets printed in the logs'
# 
# 
# run_this = PythonOperator(
#     task_id='print_the_context',
#     python_callable=print_context,
#     dag=dag,
# )
# # [END howto_operator_python]
# 
# 
# # [START howto_operator_python_kwargs]
# def my_sleeping_function(random_base):
#     """This is a function that will run within the DAG execution"""
#     time.sleep(random_base)
# 
# 
# # Generate 5 sleeping tasks, sleeping from 0.0 to 0.4 seconds respectively
# for i in range(5):
#     task = PythonOperator(
#         task_id='sleep_for_' + str(i),
#         python_callable=my_sleeping_function,
#         op_kwargs={'random_base': float(i) / 10},
#         dag=dag,
#     )
# 
#     run_this >> task
# # [END howto_operator_python_kwargs]
# 
# 
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
