#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import time
from datetime import datetime
import xml.etree.ElementTree as ET

class OaiApi:
    def __init__(self):
        """initialize api for datahub.vlaamsekunstcollectie.be"""
        self.API_URL = 'http://datahub.vlaamsekunstcollectie.be'
        self.ns0 = {'ns0':'http://www.openarchives.org/OAI/2.0/'}
        self.ns1 = {'ns1':'http://www.lido-schema.org'}
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
        if res.status_code != 200:
            print(f"WARNING: status code={res.status_code} returning empty result", flush=True)
            return [], None, 0

        root = ET.fromstring(res.text) # use res.content for bytes
        items = root.find('.//ns0:ListRecords', self.ns0)
        records = []
        for record in items:
            if 'resumptionToken' not in record.tag:
                vkc_xml = ET.tostring(record, encoding="UTF-8", xml_declaration=True).decode()
                
                header = record.find('.//ns0:header', self.ns0)
                header_identifier = header.find('.//ns0:identifier', self.ns0).text
                header_datestamp = header.find('.//ns0:datestamp', self.ns0).text

                published_tag = record.find('.//ns1:objectPublishedID', self.ns1)
                if published_tag is None:
                    published_id = None
                else:
                    published_id = published_tag.text

                records.append({
                    'xml': vkc_xml,
                    'identifier': header_identifier,
                    'published_id': published_id,
                    'datestamp': header_datestamp
                })

        resumptionTag = items.find('.//ns0:resumptionToken', self.ns0)
        if resumptionTag is not None:
            resumptionToken = resumptionTag.text
            total_records = int(resumptionTag.attrib['completeListSize'])
        else:
            total_records = len(records)

        return records, resumptionToken, total_records
