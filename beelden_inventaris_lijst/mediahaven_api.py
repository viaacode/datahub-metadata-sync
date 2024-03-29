#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  @Author: Walter Schreppers
#
#  airflow/dags/task_services/mediahaven_api.py
#
#   Make api calls to hetarchief/mediahaven
#   used for building a lookup table that
#   matches VKC OAI workID with a record in MAM
#   we only update existing mam records that have a match
#   by joining with mapping_vkc table on work_id we get a corresponding
#   fragment_id and cp_id for each vkc entry. One work_id can have multiple
#   fragment_id's associated and in this case we update all linked fragments.
#

import os
from requests import Session


class MediahavenApi:
    API_SERVER = os.environ.get(
        'MEDIAHAVEN_API',
        'https://archief-qas.viaa.be/mediahaven-rest-api'
    )
    API_USER = os.environ.get('MEDIAHAVEN_USER', 'apiUser')
    API_PASSWORD = os.environ.get('MEDIAHAVEN_PASS', 'password')

    # true/false gives different results, with false most are found,
    # but when toggling this to true we find some that we're not found when escape is off
    ESCAPE_WORK_ID = os.environ.get('ESCAPE_WORK_ID', 'false')

    def __init__(self, session=None):
        if session is None:
            self.session = Session()
        else:
            self.session = session

        print(
            f"Mediahaven initialised user = {self.API_USER} SERVER = {self.API_SERVER}")

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

    def find_by(self, department, object_key, value):
        search_matches = self.list_objects(
            department, search=f"+({object_key}:{value})")
        return search_matches

    def find_fragment(self, frag_id):
        frag_url = f"/resources/media/{frag_id}"
        return self.get_proxy(frag_url)

    def list_inventaris(self, offset=0, limit=20):
        return self.list_objects(
            search='%2B(Type:image)%2B(dc_identifier_localidsinventarisnummer:*)',
            limit=limit,
            offset=offset
        )

    def mh_mapping(self, mh_record):
        return {
            'external_id': mh_record['Administrative']['ExternalId'],
            'fragment_id': mh_record['Internal']['FragmentId'],
            'cp_id': mh_record['Dynamic']['CP_id'],
            'work_id': mh_record['Dynamic']['dc_identifier_localids']['Inventarisnummer'][0],
            'work_id_alternate': mh_record['Dynamic']['dc_identifier_localid'],
            'mimetype': mh_record['Technical']['MimeType'],
            'width_px': mh_record['Technical']['Width'],
            'height_px': mh_record['Technical']['Height']
        }

    def find_vkc_record(self, work_id):
        work_id = str(work_id)
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
                return self.mh_mapping(mh_record)
            else:
                return None
        except AssertionError:
            print("WARNING: 401 response from mediahaven api!")
            return None
        except KeyError:
            print(
                f"WARNING: find_vkc_fragment_id {work_id} response = {search_matches}")
            return None
