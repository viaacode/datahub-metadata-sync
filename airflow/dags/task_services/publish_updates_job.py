#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  @Author: Walter Schreppers
#
#  airflow/dags/task_services/publish_updates_job.py
#
#   The vkc xml docs have now been transformed and
#   are ready to publish back to mediahaven as an update request
#   we do this by pushing it to a specific rabbit mq that is implemented
#   in rabbit_publisher. We use our harvesttable and fetch BATCH_SIZE
#   rows with the HarvestTable model
#

from task_services.rabbit import RabbitClient
from psycopg2.extras import DictCursor
from task_services.harvest_table import HarvestTable

BATCH_SIZE = 200


def publish_updates_job(read_conn, update_conn):
    rabbit = RabbitClient()
    publish_count = 0
    publish_total = HarvestTable.publish_count(read_conn)
    print(f"Now sending {publish_total} mam xml records...")

    rc = read_conn.cursor('serverCursor', cursor_factory=DictCursor)
    HarvestTable.batch_select_publish_records(rc)
    while True:
        records = rc.fetchmany(size=BATCH_SIZE)
        if not records:
            break

        print(f"Fetched {len(records)} records, pushing on rabbitmq...")
        uc = update_conn.cursor(cursor_factory=DictCursor)
        for record in records:
            rabbit.publish(record)
            HarvestTable.set_synchronized(uc, record, True)

        publish_count += len(records)
        progress = round((publish_count/publish_total)*100, 1)
        print(f"Published {len(records)} records, progress {progress} %")

        update_conn.commit()  # commit all updates current batch
        uc.close()

    rc.close()
    read_conn.close()
    update_conn.close()
