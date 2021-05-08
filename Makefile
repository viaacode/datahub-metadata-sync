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
	mkdir -p python_env; \
	python3 -m venv python_env; \
	. python_env/bin/activate; \
	python3 -m pip install --upgrade pip \
	python3 -m pip install -r requirements.txt; \
	python3 -m pip install -r requirements-test.txt


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
	@. python_env/bin/activate; \
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
	export PYTHONPATH=$(pwd)/saxon/Saxon.C.API/python-saxon; \
	airflow webserver --port 8080


.PHONY: scheduler 
scheduler:
	. python_env/bin/activate; \
	export AIRFLOW_HOME=$(PWD)/airflow; \
	export PYTHONPATH=$(pwd)/saxon/Saxon.C.API/python-saxon; \
	airflow scheduler

