#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import time
from datetime import datetime

class OaiApi:
    def __init__(self):
        """initialize api for datahub.vlaamsekunstcollectie.be"""
        self.API_URL = 'http://datahub.vlaamsekunstcollectie.be'
        self.AUTH_URL = '/oauth/v2/auth'
        self.TOKEN_URL = '/oauth/v2/token'
        self.token = 'todo_fetch_with_auth_call'

        print("OaiApi initialized")

    def get_data(self, limit=20, offset=0, sort=None):
        path = self.API_URL + '/api/v1/data'
        headers={'Authorization': 'Bearer {}'.format(self.token)}

        params = {
            'limit': limit,
            'offset': offset
        }

        res = requests.get(path, params=params, headers=headers)
        print(f"status code={res.status_code}", flush=True)

        records = []
        if res.status_code == 200:
            data = res.json()
            links = data['_links'] # contains first, last, next links
            total_records = data['total']
            records = data['_embedded']['records']

        return records
