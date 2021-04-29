source python_env/bin/activate
export AIRFLOW_HOME=$(PWD)/airflow
export AIRFLOW__CORE__SQL_ALCHEMY_CON=postgresql+psycopg2://postgres:postgres@localhost:5432/airflow_development
export PYTHONPATH=$(pwd)/saxon/Saxon.C.API/python-saxon

# start the scheduler
# open a new terminal or else run webserver with ``-D`` option to run it as a daemon
airflow scheduler


