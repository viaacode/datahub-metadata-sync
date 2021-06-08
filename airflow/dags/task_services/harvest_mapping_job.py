#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  @Author: Walter Schreppers
#
#  airflow/dags/task_services/harvest_mapping_job.py
#
#   Calls mediahaven api to request all inventaris nummers
#   of images in order to build a mapping table with work_id
#   and associated frament_ids into MappingTable
#

from task_services.mediahaven_api import MediahavenApi
from task_services.mapping_table import MappingTable

#BATCH_SIZE = 500
BATCH_SIZE = 3


# find all possible images with inventaris nr's and store in db table :
def harvest_mapping_job(db_connection, full_sync=False):
    mh_api = MediahavenApi()
    offset = 0
    processed_records = 0
    result = mh_api.list_inventaris(offset, BATCH_SIZE)
    total_records = result['TotalNrOfResults']
    records = result['MediaDataList']
    mapping_count = MappingTable.count(db_connection)

    print(f"Found {total_records} inventarisnummers.")
    if not full_sync and (mapping_count == total_records):
        print("Using existing mapping table mapping_vkc.")
        db_connection.close()
        return

    # rebuild table from scratch
    print("Building new mapping_vkc mapping table...")
    MappingTable.truncate(db_connection)

    while(processed_records < total_records and len(records) > 0):
        for mh_record in records:
            mapped_ids = mh_api.mh_mapping(mh_record)
            MappingTable.insert(db_connection, mapped_ids)
            processed_records += 1

        print(f"processed {len(records)} records, offset={offset}")

        offset += BATCH_SIZE
        result = mh_api.list_inventaris(offset, BATCH_SIZE)
        records = result['MediaDataList']

        # add this break to create a smaller pytest-recording
        # if offset > 6:
        #    break

    db_connection.commit()
    db_connection.close()
