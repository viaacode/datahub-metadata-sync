#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  @Author: Walter Schreppers
#
#  airflow/dags/task_services/harvest_vkc_job.py
#
#   Calls vkc_api in order to store vlaamsekunstcollectie xml documents
#   into postgres db using db_connection
#

from psycopg2.extras import DictCursor
from task_services.harvest_table import HarvestTable
from task_services.vkc_api import VkcApi


def harvest_vkc_job(db_connection, full_sync):
    if full_sync:
        print("VKC full sync started...")
        HarvestTable.truncate(db_connection)
    else:
        print("VKC delta sync started...")

    cursor = db_connection.cursor(cursor_factory=DictCursor)
    last_synced = HarvestTable.get_max_datestamp(cursor)

    api = VkcApi()
    records, token, total = api.list_records(from_filter=last_synced)

    total_count = len(records)

    while len(records) > 0:
        progress = round((total_count/total)*100, 1)

        print(f"Saving {len(records)} of {total} records {progress} %")
        for record in records:
            if record['work_id'] is not None:
                # for a few records, work_id is missing, we omit these
                HarvestTable.insert(cursor, record)
            else:
                print(
                    f"Skipping record with empty work_id record={record}", flush=True)

        db_connection.commit()  # commit batch of inserts

        if total_count >= total:
            break  # exit loop, we have all records from vkc

        # fetch next batch of records with api
        records, token, total = api.list_records(resumptionToken=token)
        total_count += len(records)

    cursor.close()
    db_connection.close()
