#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  @Authors: Rudolf, Matthias, Walter
#
#   airflow/dags/task_services/rabbit.py
#
#   Utility class that wraps pika and uses env vars to
#   set rabbit mq host, port, user, pass, prefetch, queue_name
#
#   publish method: publishes our record with
#   converted xml to the mam-update-requests micro service
#   using send_message.
#

import time
import pika
import os
import json


class RabbitClient:
    def __init__(self):
        self.RABBIT_HOST = os.environ.get('RABBIT_HOST', 'url_here')
        self.RABBIT_PORT = os.environ.get('RABBIT_PORT', 'port_here')

        self.RABBIT_USER = os.environ.get('RABBIT_USER', 'user')
        self.RABBIT_PASS = os.environ.get('RABBIT_PASS', 'pw')

        self.RABBIT_QUEUE = os.environ.get(
            'RABBIT_QUEUE', 'mam-update-requests')

        self.credentials = pika.PlainCredentials(
            self.RABBIT_USER, self.RABBIT_PASS
        )

        print("RabbitClient connecting...")
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=self.RABBIT_HOST,
                port=self.RABBIT_PORT,
                credentials=self.credentials,
            )
        )

        self.channel = self.connection.channel()
        self.prefetch_count = int(os.environ.get('RABBIT_PREFETCH', '1'))
        print("RabbitClient ready.")

    def publish(self, record):
        """publish update request to rabbitmq"""
        update_request = {
            "correlation_id": record['work_id'],
            "fragment_id": record['fragment_id'],
            "cp_id": record['cp_id'],
            "data": record['mam_xml']
        }

        self.send_message(
            routing_key='mam-update-requests',
            body=json.dumps(update_request),
        )

    def send_message(self, routing_key, body, exchange=""):
        try:
            self.channel.basic_publish(
                exchange=exchange, routing_key=routing_key, body=body,
            )

        except pika.exceptions.AMQPConnectionError as error:
            raise error

    def listen(self, on_message_callback, queue=None):
        if queue is None:
            queue = self.RABBIT_QUEUE

        try:
            while True:
                try:
                    channel = self.connection.channel()

                    channel.basic_qos(
                        prefetch_count=self.prefetch_count, global_qos=False
                    )
                    channel.basic_consume(
                        queue=queue, on_message_callback=on_message_callback
                    )

                    channel.start_consuming()
                except pika.exceptions.StreamLostError:
                    print("WARNING: RMQBridge lost connection, reconnecting...")
                    time.sleep(3)
                except pika.exceptions.ChannelWrongStateError:
                    print("WARNING: RMQBridge wrong state in channel, reconnecting...")
                    time.sleep(3)
                except pika.exceptions.AMQPHeartbeatTimeout:
                    print("WARNING: RMQBridge heartbeat timed out, reconnecting...")
                    time.sleep(3)

        except KeyboardInterrupt:
            self.channel.stop_consuming()

        self.connection.close()
