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
                return search_matches['MediaDataList'][0]
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
        

    def build_mh_lookup_table(self):
        BATCH_SIZE = 500
        offset = 0
        result = self.list_inventaris(offset, BATCH_SIZE)
        lookup_table = {}

        total_records = result['TotalNrOfResults']
        records = result['MediaDataList']
        print(f"found {total_records} matches")
        processed_records = 0

        while(processed_records < total_records and len(records) > 0):
            for mh_record in records:
                fragment_id = mh_record['Internal']['FragmentId']
                cp_id = mh_record['Dynamic']['CP_id']
                work_id = mh_record['Dynamic']['dc_identifier_localids']['Inventarisnummer'][0] # issue on qas this has . and on prd it has underscore
                work_id_alternate = mh_record['Dynamic']['dc_identifier_localid'] # has underscores (but matched less on prd)

                lookup_table[work_id] = {
                    'fragment_id': fragment_id,
                    'cp_id': cp_id,
                    'work_id': work_id,
                    'work_id_alternate': work_id_alternate
                }

                processed_records += 1
                # print(f"{work_id} -> {fragment_id}") -> on qas we see some duplicates in work_id, but luckily not
                # the ones that come from vkc.
                # 0000.GRO0220.I -> 4ad07fc61ae7488aaafd2b0322fe9295671ee1...
                # S/57/B -> 663b976e6b5f4f30979fceba2ab657906bb25014503f4...
                # S/57/B -> 5d20658368394ebe882141dc7b7efcc29d99909b24da...
                # S/57/B -> fe82f8f85f2543059a998727fd6a6a69ddc25234f22...
                # S/57/B -> a14a8d623d9e484fbf486feab430832ddeccbc5352...
            print(f"processed {len(records)} records, offset={offset}")

            offset += BATCH_SIZE
            result = self.list_inventaris(offset, BATCH_SIZE)
            records = result['MediaDataList']

        return lookup_table

# for qas we see this table works for our 3 work_ids, to be determined if this strategy also applies
# in production where we have 32k records instead of 180 like on qas:
# >>> from airflow.dags.task_services.mediahaven_api import MediahavenApi; api=MediahavenApi()
# >>> res = api.build_mh_lookup_table()
# >>> res['2253']
# {'fragment_id': '19155a35a9e244f7bbf2f996b3f43e75a68bb6bdbc9d4ab3aab6f25715dc3c123aa38117d7d341f091f4cec5bbf64d9a', 'cp_id': 'OR-4t6f29d', 'work_id': '2253'}
# >>> res['23038']
# {'fragment_id': '318b7bee74d5457e99b75cf3853362e16194322085b34292a333448bf0197f1bcd430d9561a941bfab8fe647d186f891', 'cp_id': 'OR-4t6f29d', 'work_id': '23038'}
# >>> res['0000.GRO0220.I']
# {'fragment_id': '4ad07fc61ae7488aaafd2b0322fe9295671ee12df32d4c16bbdbbd5f8cbc5743e72d19e5e0c3428d8ee5cdfec3d7dc45', 'cp_id': 'OR-4t6f29d', 'work_id': '0000.GRO0220.I'}
