source python_env/bin/activate
export AIRFLOW_HOME=$(PWD)/airflow

# depending on what you need, run tests in sqlite, or have real postgres export these:
export AIRFLOW__CORE__SQL_ALCHEMY_CONN=postgresql+psycopg2://postgres:postgres@localhost:5432/airflow_development
#export AIRFLOW__CORE__SQL_ALCHEMY_CONN=sqlite:///airflow/airflow.db


# initialize the database
airflow db init

# create admin user (requires to type password here)
airflow users create \
    --username admin \
    --firstname Walter \
    --lastname Schreppers \
    --role Admin \
    --email walter@schreppers.com

