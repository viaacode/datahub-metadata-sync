source python_env/bin/activate
export AIRFLOW_HOME=$(PWD)/airflow
export AIRFLOW__CORE__SQL_ALCHEMY_CON=postgresql+psycopg2://postgres:postgres@localhost:5432/airflow_development

# initialize the database
airflow db init

# create admin user (requires to type password here)
airflow users create \
    --username admin \
    --firstname Walter \
    --lastname Schreppers \
    --role Admin \
    --email walter@schreppers.com

