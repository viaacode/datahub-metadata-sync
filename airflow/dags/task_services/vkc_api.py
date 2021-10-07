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
                header_datestamp = header.find(
                    './/ns0:datestamp', self.ns0).text
                work_id = self._get_work_id(record, header)
                min_w, max_w = self._get_widths(record)
                vd_actor_earliest, vd_actor_latest = self._get_vital_dates_actor(
                    record)

                records.append({
                    'xml': vkc_xml,
                    'work_id': work_id,
                    'datestamp': header_datestamp,
                    'aanbieder': self._get_aanbieder(record),
                    'min_breedte_cm': min_w,
                    'max_breedte_cm': max_w,
                    'vd_actor_earliest': vd_actor_earliest,
                    'vd_actor_latest': vd_actor_latest,
                    'maker_name': self._get_maker_name(record)
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

        # print(f"VkcApi::list_records params = {params}")

        return params

    def _get_widths(self, record):
        metadata = record.find('.//ns0:metadata', self.ns0)
        measurements = metadata.findall('.//{}/{}/{}/{}'.format(
            'ns1:descriptiveMetadata',
            'ns1:objectIdentificationWrap',
            'ns1:objectMeasurementsWrap',
            'ns1:objectMeasurementsSet',
        ),
            self.ns1
        )

        min_breedte = 0
        max_breedte = 0
        breedte = 0

        for m in measurements:
            mset = m.find(
                './/ns1:objectMeasurements/ns1:measurementsSet', self.ns1)
            #  mextent is inconsistent to determine we use min/max instead
            #  mextent = m.find('.//ns1:objectMeasurements/ns1:extentMeasurements', self.ns1)

            if mset is not None and len(mset) > 0 and (
                mset[0].text == 'Breedte' or mset[0].text == 'breedte'
            ):
                try:
                    breedte = float(mset[2].text)
                except ValueError:
                    breedte = 0
                    print(
                        f'warning could not parse breedte = {mset[2].text}, using 0 as value')
                except TypeError:
                    breedte = 0

            if breedte <= min_breedte or min_breedte == 0:
                min_breedte = breedte

            if breedte >= max_breedte:
                max_breedte = breedte

        return min_breedte, max_breedte

    def _get_actors(self, metadata):
        return metadata.findall('.//{}/{}/{}/{}/{}/{}/{}'.format(
            'ns1:descriptiveMetadata',
            'ns1:eventWrap',
            'ns1:eventSet',
            'ns1:event',
            'ns1:eventActor',
            'ns1:actorInRole',
            'ns1:actor'
        ),
            self.ns1
        )

    def _get_vital_dates_actor(self, record):
        metadata = record.find('.//ns0:metadata', self.ns0)

        # for now, just return dates on first actor we find
        for actor in self._get_actors(metadata):
            earliest_date = '' 
            latest_date = ''

            earliest_date_node = actor.find(
                './/ns1:vitalDatesActor/ns1:earliestDate',
                self.ns1
            )

            if earliest_date_node:
                earliest_date = earliest_date_node.text

            latest_date_node = actor.find(
                './/ns1:vitalDatesActor/ns1:latestDate',
                self.ns1
            )

            if latest_date_node:
                latest_date = latest_date_node.text

            return earliest_date, latest_date
    
        return '',''


    def _get_maker_name(self, record):
        metadata = record.find('.//ns0:metadata', self.ns0)
        # for now, just return first actor name that we find
        # we do however make sure already we have the 'alternate' attribute tag
        for actor in self._get_actors(metadata):
            worker_names = actor.findall(
                './/ns1:nameActorSet/ns1:appellationValue', self.ns1)

            if not worker_names:
                return None

            for wn in worker_names:
                if wn.attrib['{http://www.lido-schema.org}pref'] == 'alternate':
                    return wn.text

    def _get_aanbieder(self, record):
        metadata = record.find('.//ns0:metadata', self.ns0)
        legal_appelation = metadata.find('.//{}/{}/{}/{}/{}'.format(
            'ns1:administrativeMetadata',
            'ns1:recordWrap',
            'ns1:recordSource',
            'ns1:legalBodyName',
            'ns1:appellationValue'
        ),
            self.ns1
        )
        aanbieder = legal_appelation.text

        return aanbieder

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
