export AIRFLOW_HOME=$(PWD)/airflow
export AIRFLOW__CORE__SQL_ALCHEMY_CON=postgresql+psycopg2://postgres:postgres@localhost:5432/airflow_development

source python_env/bin/activate

echo "make sure you have start_scheduler.sh and start_webserver.sh running before executing this"

# run your first task instance
airflow tasks run example_bash_operator runme_0 2015-01-01
# run a backfill over 2 days
airflow dags backfill example_bash_operator \
    --start-date 2015-01-01 \
    --end-date 2015-01-02

