#!/usr/bin/env python
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
        return self.get_proxy(f"/resources/media?q={search}&startIndex={offset}&nrOfResults={limit}")

    def find_by(self, object_key, value):
        search_matches = self.list_objects(search=f"+({object_key}:{value})")
        return search_matches

    def find_vkc_record(self, work_id):
        try:
            localid = work_id.replace('.','_').replace("/","\\/")
            search_matches = self.list_objects(search=f'+(dc_identifier_localidsinventarisnummer:"{localid}")')
            if search_matches['TotalNrOfResults']>=1:
                return search_matches['MediaDataList'][0]
            else:
                return None
        except AssertionError:
            print("WARNING: 401 response from mediahaven api!")
            return None
        except KeyError:
            print(f"WARNING: find_vkc_fragment_id {work_id} response = {search_matches}")
            return None


