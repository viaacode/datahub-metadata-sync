NAME := ldap2db
FOLDERS := ./app/ ./tests/

.DEFAULT_GOAL := help


.PHONY: help
help:
	@echo "Available make commands:"
	@echo ""
	@echo "  install     install packages and prepare environment"
	@echo "  clean       remove all temporary files"
	@echo "  lint        run the code linters"
	@echo "  format      reformat code"
	@echo "  test        run all the tests"
	@echo "  dockertest  run all the tests in docker image like jenkins"
	@echo "  coverage    run tests and generate coverage report"
	@echo "  server      start airflow webserver port 8080"
	@echo "  scheduler   start airflow scheculer to run dags"
	@echo ""


.PHONY: install
install:
	mkdir -p python_env && \
	python3 -m venv python_env && \
	. python_env/bin/activate && \
	python3 -m pip install --upgrade pip; \
	python3 -m pip install -r requirements.txt; \
	python3 -m pip install -r requirements-test.txt; \
	cd saxon/Saxon.C.API/python-saxon && \
	python3 saxon-setup.py build_ext -if && \
	export PYTHONPATH=$PYTHONPATH:$(pwd) && \
	cd ../../../



.PHONY: clean
clean:
	find . -type d -name "__pycache__" | xargs rm -rf {}; \
	rm -rf .coverage htmlcov


.PHONY: lint
lint:
	@. python_env/bin/activate; \
	flake8 --max-line-length=120 --exclude=.git,python_env,__pycache__,saxon


.PHONY: format
format:
	@. python_env/bin/activate; \
	autopep8 --in-place -r airflow; \
	autopep8 --in-place -r tests;

.PHONY: test
test:
	@. python_env/bin/activate && \
	export AIRFLOW_HOME=$(PWD)/airflow && \
	export PYTHONPATH=$(PWD)/saxon/Saxon.C.API/python-saxon && \
	unset AIRFLOW__CORE__SQL_ALCHEMY_CONN && \
	airflow db init && \
	sqlite3 airflow/airflow.db "update connection set conn_type='sqlite', host='${PWD}/airflow/airflow.db', schema=NULL, login=NULL, password=NULL, port=NULL, extra=NULL, is_encrypted=0, is_extra_encrypted=0 where conn_id='postgres_default';" ".exit" && \
	python -m pytest tests


.PHONY: dockertest
dockertest:
	docker build . -t ldap2db; \
	docker container run --name ldap2db --env-file .env.example --entrypoint python "ldap2db" "-m" "pytest"


.PHONY: coverage
coverage:
	@. python_env/bin/activate; \
	python -m pytest --cov-config=.coveragerc --cov . .  --cov-report html --cov-report term --ignore saxon


.PHONY: server
server:
	. python_env/bin/activate; \
	export AIRFLOW_HOME=$(PWD)/airflow; \
	export PYTHONPATH=$(PWD)/saxon/Saxon.C.API/python-saxon; \
	airflow webserver --port 8080


.PHONY: scheduler 
scheduler:
	. python_env/bin/activate; \
	export AIRFLOW_HOME=$(PWD)/airflow; \
	export PYTHONPATH=$(PWD)/saxon/Saxon.C.API/python-saxon; \
	airflow scheduler


