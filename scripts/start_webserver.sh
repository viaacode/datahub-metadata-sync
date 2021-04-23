source python_env/bin/activate
export AIRFLOW_HOME=$(PWD)/airflow
export AIRFLOW__CORE__SQL_ALCHEMY_CON=postgresql+psycopg2://postgres:postgres@localhost:5432/airflow_development

echo "visit localhost:8080 in the browser and use the admin account"
echo "created to login. Enable the example_bash_operator dag in the home page"
echo "also use scripts/start_scheduler.sh"


# start the web server, default port is 8080
airflow webserver --port 8080

