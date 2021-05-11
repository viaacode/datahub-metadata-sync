#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  @Author: Walter Schreppers
#
#  airflow/dags/task_services/vkc_api.py
#
#   Fetch xml records from datahub.vlaamsekunstcollectie.be
#   we also handle pagination with resumptionToken here
#

import requests
import xml.etree.ElementTree as ET
from datetime import timezone


class VkcApi:
    def __init__(self):
        """initialize api for datahub.vlaamsekunstcollectie.be"""
        self.API_URL = 'http://datahub.vlaamsekunstcollectie.be'
        self.ns0 = {'ns0': 'http://www.openarchives.org/OAI/2.0/'}
        self.ns1 = {'ns1': 'http://www.lido-schema.org'}
        print("VkcApi initialized")

    def list_records(self, from_filter=None, prefix='oai_lido', resumptionToken=None):
        path = self.API_URL + '/oai/'
        res = requests.get(
            path,
            params=self._list_params(
                from_filter, prefix, resumptionToken
            )
        )

        if res.status_code != 200:
            print(
                f"WARNING: status code={res.status_code}, returning empty result",
                flush=True
            )
            return [], None, 0

        root = ET.fromstring(res.text)
        items = root.find('.//ns0:ListRecords', self.ns0)
        if items is None:
            return [], None, 0

        records = []
        for record in items:
            if 'resumptionToken' not in record.tag:
                vkc_xml = ET.tostring(
                    record,
                    encoding="UTF-8",
                    xml_declaration=True
                ).decode()

                header = record.find('.//ns0:header', self.ns0)
                header_datestamp = header.find('.//ns0:datestamp', self.ns0).text
                work_id = self._get_work_id(record, header)

                records.append({
                    'xml': vkc_xml,
                    'work_id': work_id,
                    'datestamp': header_datestamp
                })

        resumptionTag = items.find('.//ns0:resumptionToken', self.ns0)
        if resumptionTag is not None:
            resumptionToken = resumptionTag.text
            total_records = int(resumptionTag.attrib['completeListSize'])
        else:
            total_records = len(records)

        return records, resumptionToken, total_records

    def _list_params(self, from_filter, prefix, resumptionToken):
        params = {
            'verb': 'ListRecords',
        }

        if from_filter is None:
            from_filter = '2011-06-01T00:00:00Z'
        else:
            # the vkc api does not support +01:00 format, convert to utc:
            from_filter = from_filter.astimezone(
                tz=timezone.utc
            ).isoformat().replace("+00:00", "Z")

        if not resumptionToken:
            params['from'] = from_filter
            params['metadataPrefix'] = prefix
        else:
            params['resumptionToken'] = resumptionToken

        print(f"VkcApi::list_records params = {params}")

        return params

    def _get_work_id(self, record, header):
        metadata = record.find('.//ns0:metadata', self.ns0)
        work_tag = metadata.find(
            './/{}/{}/{}/{}/{}'.format(
                'ns1:descriptiveMetadata',
                'ns1:objectIdentificationWrap',
                'ns1:repositoryWrap',
                'ns1:repositorySet',
                'ns1:workID'
            ),
            self.ns1
        )

        if work_tag is None:
            identifier = header.find('.//ns0:identifier', self.ns0).text
            print(
                f"VKC record found without work_id, identifier: {identifier}"
            )
            return None
        else:
            return work_tag.text
