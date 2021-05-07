#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  @Author: Walter Schreppers
#
#  airflow/dags/task_services/rabbit_publisher.py
#
#   Publish a record with converted xml to the mam-update-requests
#   queue using the rabbit client

from .rabbit import RabbitClient
import json


class RabbitPublisher:
    def __init__(self):
        """connect to rabbitmq"""
        print("RabbitPublisher connecting...")
        self.rabbit_client = RabbitClient()
        print("RabbitPublisher ready")

    def publish(self, record):
        """publish to rabbitmq"""
        update_request = {
            "correlation_id": record['work_id'],  # uuid.uuid4().hex,
            "fragment_id": record['fragment_id'],
            "cp_id": record['cp_id'],
            "data": record['mam_xml']
        }

        print(
            "publishing record with work_id={} fragment_id={} cp_id={}".format(
                record['work_id'],
                record['fragment_id'],
                record['cp_id']
            ))

        self.rabbit_client.send_message(
            routing_key='mam-update-requests',
            body=json.dumps(update_request),
        )
