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
    # Voor v2 is endpoint hier /mediahaven-rest-api/v2/resources/
    # en met oauth ipv basic auth
    API_SERVER = os.environ.get(
        'MEDIAHAVEN_API',
        'https://archief-qas.viaa.be/mediahaven-rest-api'
    )
    API_USER = os.environ.get('MEDIAHAVEN_USER', 'apiUser')
    API_PASSWORD = os.environ.get('MEDIAHAVEN_PASS', 'password')
    DEPARTMENT_ID = os.environ.get(
        'DEPARTMENT_ID',
        'dd111b7a-efd0-44e3-8816-0905572421da'
    )

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
            # TODO: currently this breaks calls, re-enable later
            # for better compatibility with v2:
            # 'Accept': 'application/vnd.mediahaven.v2+json'
        }

        response = self.session.get(
            url=get_url,
            headers=headers,
            auth=(self.API_USER, self.API_PASSWORD)
        )

        return response.json()

    def list_objects(self, search='', offset=0, limit=25):
        return self.get_proxy(f"/resources/media?q={search}&startIndex={offset}&nrOfResults={limit}")

    def find_by(self, object_key, value):
        search_matches = self.list_objects(search=f"+({object_key}:{value})")
        return search_matches

    def vkc_record_exists(self, work_id):
        # example 1976.GRO0815.I, replace . with _ or find multiple ones
        # resources/media/?q=%2B(dc_identifier_localid%3A%221976_GRO0815_I%22)
        # alternatief rechtstreeks met work_id maar dan heb je meer results:
        # https://archief.viaa.be/mediahaven-rest-api/resources/media/?q=%2B(%221976.GRO0815.I%22)
        localid = work_id.replace('.','_')
        search_matches = self.list_objects(search=f'+(dc_identifier_localid:{localid})')

        return len(search_matches)>=1


