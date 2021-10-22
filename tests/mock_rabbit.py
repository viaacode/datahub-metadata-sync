#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  @Author: Walter Schreppers
#
#  tests/mock_rabbit.py
#
#   MockRabbitClient to mock out connections to rabbit mq
#


class MockRabbitClient:
    def __init__(self):
        self.publish_history = []

    def publish(self, record):
        self.publish_history.append(record)
