#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from .rabbit import RabbitClient

class RabbitPublisher:
    def __init__(self):
        """connect to rabbitmq"""
        print("RabbitPublisher initialized")
        self.rabbit_client = RabbitClient()

    def publish(self, record):
        """publish to rabbitmq"""
        record_id = record[0]
        mam_xml = record[2]
        print(f"push record with id={record_id} to rabbitmq mam_xml={mam_xml[0:20]}", flush=True)


# inspiration for publishing on rmq with mam-update service, see slack comments rudolf here:
# https://github.com/viaacode/mam-update-service
# gewoon iets gelijk example 1 doen
# 
# of
# 
# https://github.com/viaacode/vrt-events-metadata/commit/e61e550aa572c707f418e7398e73cc70ea709321
# 
# Hier zat een python voorbeeldje, maar is ondertussen weg :wink:


    def send_to_rabbit(self, record):
        # 5. Update mediahaven fragement with received metadata
        update_request = {
            "correlation_id": uuid.uuid4().hex,
            "fragment_id": fragment_id,
            "cp_id": mtd_cfg["transformation"],
            "data": transformation_response.text,
        }

        print(f"sending message to update service {update_request}")

        self.rabbit_client.send_message(
            routing_key=self.config["mam-update-service"]["queue"],
            body=json.dumps(update_request),
        )

        channel.basic_ack(delivery_tag=method.delivery_tag)
