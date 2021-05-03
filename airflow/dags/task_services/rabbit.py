#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import pika


class RabbitClient:
    def __init__(self):
        configParser = ConfigParser()
        self.rabbitConfig = configParser.app_cfg["rabbitmq"]

        self.RABBIT_USER = 'todo'
        self.RABBIT_PASS = 'todo'
        self.RABBIT_HOST = 'todo'
        self.RABBIT_PORT = 'todo'
        self.RABBIT_QUEUE = 'todo'
        self.RABBIT_PREFETCH = 1

        self.credentials = pika.PlainCredentials(
            self.RABBIT_USER, self.RABBIT_PASS
        )

        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=self.RABBIT_HOST,
                port=self.RABBIT_PORT,
                credentials=self.credentials,
            )
        )

        self.channel = self.connection.channel()
        self.prefetch_count = int(self.RABBIT_PREFETCH)

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
