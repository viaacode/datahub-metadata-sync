class MockRabbitClient:
    def __init__(self):
        self.publish_history = []

    def publish(self, record):
        self.publish_history.append(record)
        # routing_key='routingkey', body='body'
        # self.publish_history.append({
        #     'routing_key': routing_key,
        #     'body': body
        # })
