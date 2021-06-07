#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  @Author: Walter Schreppers
#
#  airflow/dags/task_services/transform_xml_job.py
#
#   Uses transformer_process wrapper around
#   XmlTransformer to convert batches of BATCH_SIZE
#   of xml's in vkc_xml format into mediahaven xml format
#   for the transformation look in dags/resources/main.xslt
#

from psycopg2.extras import DictCursor
from task_services.harvest_table import HarvestTable
# instead of using our xmltransformer directly we use the
# transformer_process wrapper to workaround a memleak in saxonc
# from task_services.xml_transformer import XmlTransformer
from task_services.transformer_process import xml_convert

BATCH_SIZE = 200


def transform_xml_job(read_conn, update_conn):
    transform_count = 0
    transform_total = HarvestTable.transform_count(read_conn)
    print(f"Now transforming {transform_total} xml records...")

    # tr = XmlTransformer()
    rc = read_conn.cursor('serverCursor', cursor_factory=DictCursor)
    HarvestTable.batch_select_transform_records(rc)
    while True:
        records = rc.fetchmany(size=BATCH_SIZE)
        if not records:
            break

        transform_count += len(records)
        progress = round((transform_count/transform_total)*100, 1)
        uc = update_conn.cursor(cursor_factory=DictCursor)

        # use forked process to convert a whole batch of records
        # we can revert to using tr.convert once the saxonc memory leak
        # is fixed. For now converting a batch and then closing the forked
        # process and starting a new one seems to work well
        xpos = 0
        vkc_xml_batch = [record['vkc_xml'] for record in records]
        mam_xml_batch = xml_convert(vkc_xml_batch)

        for record in records:
            # mam_xml = tr.convert(record['vkc_xml'])
            mam_xml = mam_xml_batch[xpos]
            HarvestTable.update_mam_xml(uc, record, mam_xml)
            xpos += 1

        update_conn.commit()  # commit all updates current batch
        uc.close()
        print(f"Processed {len(records)} records, progress {progress} %")

    rc.close()
    read_conn.close()
    update_conn.close()
