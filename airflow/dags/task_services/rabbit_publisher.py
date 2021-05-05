#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from .rabbit import RabbitClient

class RabbitPublisher:
    def __init__(self):
        """connect to rabbitmq"""
        print("RabbitPublisher connecting...")
        self.rabbit_client = RabbitClient()
        print("RabbitPublisher ready")

    def publish(self, record):
        """publish to rabbitmq"""
        update_request = {
            "correlation_id": record['work_id'],# uuid.uuid4().hex,
            "fragment_id": record['fragment_id'],
            "cp_id": record['cp_id'],
            "data": record['mam_xml']
        }

        print(
            "publishing record with work_id={} fragment_id={} cp_id={} data={}".format(
            record['work_id'],
            record['fragment_id'],
            record['cp_id']
        ))

        self.rabbit_client.send_message(
            routing_key='mam-update-requests',
            body=json.dumps(update_request),
        )

        channel.basic_ack(delivery_tag=method.delivery_tag)

    # inspiration for publishing on rmq with mam-update service, see slack comments rudolf here:
    # https://github.com/viaacode/mam-update-service
    # gewoon iets gelijk example 1 doen
    # of
    # https://github.com/viaacode/vrt-events-metadata/commit/e61e550aa572c707f418e7398e73cc70ea709321
