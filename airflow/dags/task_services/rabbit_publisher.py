#!/usr/bin/env python3
# -*- coding: utf-8 -*-


class RabbitPublisher:
    def __init__(self):
        """connect to rabbitmq"""
        print("RabbitPublisher initialized")

    def publish(self, record):
        """publish to rabbitmq"""
        record_id = record[0]
        mam_xml = record[2]
        print(f"push record with id={record_id} to rabbitmq mam_xml={mam_xml[0:20]}", flush=True)

