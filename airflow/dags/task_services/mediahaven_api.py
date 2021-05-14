#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  @Author: Walter Schreppers
#
#  airflow/dags/task_services/mediahaven_api.py
#
#   Make api calls to hetarchief/mediahaven
#   used for checking if VKC OAI record was already synced before

import os
from requests import Session


class MediahavenApi:
    API_SERVER = os.environ.get(
        'MEDIAHAVEN_API',
        'https://archief-qas.viaa.be/mediahaven-rest-api'
    )
    API_USER = os.environ.get('MEDIAHAVEN_USER', 'apiUser')
    API_PASSWORD = os.environ.get('MEDIAHAVEN_PASS', 'password')

    ESCAPE_WORK_ID = os.environ.get('ESCAPE_WORK_ID', 'false')

    def __init__(self, session=None):
        self.lookup_table = {}
        if session is None:
            self.session = Session()
        else:
            self.session = session

    # generic get request to mediahaven api
    def get_proxy(self, api_route):
        get_url = f"{self.API_SERVER}{api_route}"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/vnd.mediahaven.v2+json'
        }

        response = self.session.get(
            url=get_url,
            headers=headers,
            auth=(self.API_USER, self.API_PASSWORD)
        )
        assert response.status_code != 401
        return response.json()

    def list_objects(self, search='', offset=0, limit=25):
        return self.get_proxy(
            f"/resources/media/?q={search}&startIndex={offset}&nrOfResults={limit}"
        )

    def find_by(self, object_key, value):
        search_matches = self.list_objects(search=f"+({object_key}:{value})")
        return search_matches

    def mh_result(self, mh_record):
        # other possible field combos to investigate:
        # object_number, object_nummer, objectNumber, objectnummer
        return {
            'fragment_id': mh_record['Internal']['FragmentId'],
            'cp_id': mh_record['Dynamic']['CP_id'],
            'work_id': mh_record['Dynamic']['dc_identifier_localids']['Inventarisnummer'][0],

            # has underscores (but matched less on prd)
            'work_id_alternate': mh_record['Dynamic']['dc_identifier_localid']
        }

    def find_vkc_record(self, work_id):
        try:
            if self.ESCAPE_WORK_ID == 'true':
                # this working on production:
                localid = work_id.replace('.', '_').replace("/", "\\/")
            else:
                # for qas we skip the replace of .
                localid = work_id.replace("/", "\\/")

            search_matches = self.list_objects(
                search=f'%2B(dc_identifier_localidsinventarisnummer:"{localid}")'
            )
            if search_matches['TotalNrOfResults'] >= 1:
                mh_record = search_matches['MediaDataList'][0]
                return self.mh_result(mh_record)
            else:
                return None
        except AssertionError:
            print("WARNING: 401 response from mediahaven api!")
            return None
        except KeyError:
            print(
                f"WARNING: find_vkc_fragment_id {work_id} response = {search_matches}")
            return None

    def list_inventaris(self, offset=0, limit=20):
        return self.list_objects(
            search='%2B(Type:image)%2B(dc_identifier_localidsinventarisnummer:*)',
            limit=limit,
            offset=offset
        )

    def build_lookup_table(self):
        print("Building lookup table...")
        BATCH_SIZE = 500
        offset = 0
        result = self.list_inventaris(offset, BATCH_SIZE)
        self.lookup_table = {}

        total_records = result['TotalNrOfResults']
        records = result['MediaDataList']
        print(f"found {total_records} matches")
        processed_records = 0

        while(processed_records < total_records and len(records) > 0):
            for mh_record in records:
                mh_res = self.mh_result(mh_record)
                self.lookup_table[mh_res['work_id']] = mh_res
                processed_records += 1

            print(f"processed {len(records)} records, offset={offset}")

            offset += BATCH_SIZE
            result = self.list_inventaris(offset, BATCH_SIZE)
            records = result['MediaDataList']

        return self.lookup_table

    def lookup_vkc_record(self, work_id):
        return self.lookup_table.get(work_id, None)
