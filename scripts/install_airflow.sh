# make new virtual env
mkdir -p python_env
python3 -m venv python_env
source python_env/bin/activate
# do this to get wheel/bin version of cryptography
python3 -m pip install --upgrade pip

# install from pypi using pip
# python3 -m pip install apache-airflow
python3 -m pip install -r requirements.txt
python3 -m pip install -r requirements-test.txt

export AIRFLOW_HOME=$(PWD)/airflow
export AIRFLOW__CORE__SQL_ALCHEMY_CON=postgresql+psycopg2://postgres:postgres@localhost:5432/airflow_development


