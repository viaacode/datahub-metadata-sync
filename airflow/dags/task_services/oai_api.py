#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import time
from datetime import datetime
import xml.etree.ElementTree as ET

class OaiApi:
    def __init__(self):
        """initialize api for datahub.vlaamsekunstcollectie.be"""
        # fetching data with oai/xml needs no auth at all.
        #self.API_URL = 'http://datahub.vlaamsekunstcollectie.be'
        #self.AUTH_URL = '/oauth/v2/auth'
        #self.TOKEN_URL = '/oauth/v2/token'
        #self.token = 'todo_fetch_with_auth_call'

        self.API_URL = 'http://datahub.vlaamsekunstcollectie.be'


        print("OaiApi initialized")

    def list_records(self, from_filter='2011-06-01T00:00:00Z', prefix='oai_lido', resumptionToken=None):
        path = self.API_URL + '/oai/'
        params = {
            'verb': 'ListRecords',
        }

        if not resumptionToken:
            params['from'] = from_filter
            params['metadataPrefix'] = prefix
        else:
            params['resumptionToken'] = resumptionToken

        res = requests.get(path, params=params)
        records = []
        total_records = 0
        if res.status_code == 200:
            root = ET.fromstring(res.text) # use res.content for bytes
            ns = {'d':'http://www.openarchives.org/OAI/2.0/'}
            items = root.find('.//d:ListRecords', ns)
            resumptionTag = items.find('.//d:resumptionToken', ns)

            if resumptionTag is not None:
                resumptionToken = resumptionTag.text
                total_records = int(resumptionTag.attrib['completeListSize'])

            for record in items:
                if 'resumptionToken' not in record.tag:
                    records.append(
                        ET.tostring(record, encoding="UTF-8", xml_declaration=True).decode()
                    )
        else:
            print(f"WARNING: status code={res.status_code}", flush=True)

        return records, resumptionToken, total_records
