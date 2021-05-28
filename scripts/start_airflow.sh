#!/bin/bash
airflow scheduler -D &
airflow webserver --port 8080


