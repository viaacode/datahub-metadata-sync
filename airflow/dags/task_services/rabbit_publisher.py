#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  @Author: Walter Schreppers
#
#  airflow/dags/task_services/rabbit_publisher.py
#
#   Publish a record with converted xml to the mam-update-requests
#   queue using the rabbit client
#

from task_services.rabbit import RabbitClient
import json


class RabbitPublisher:
    def __init__(self):
        """connect to rabbitmq"""
        print("RabbitPublisher connecting...")
        self.rabbit_client = RabbitClient()
        print("RabbitPublisher ready")

    def publish(self, record):
        """publish update request to rabbitmq"""
        update_request = {
            "correlation_id": record['work_id'],
            "fragment_id": record['fragment_id'],
            "cp_id": record['cp_id'],
            "data": record['mam_xml']
        }

        # good for debug, but when publishing 12k records the log page of task
        # becomes too large.
        # print("publishing update: correlation_id {} fragment_id {} cp_id {}".format(
        #     update_request['correlation_id'],
        #     update_request['fragment_id'],
        #     update_request['cp_id']
        # ))

        self.rabbit_client.send_message(
            routing_key='mam-update-requests',
            body=json.dumps(update_request),
        )
