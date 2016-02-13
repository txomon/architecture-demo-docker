from __future__ import absolute_import

import argparse
import pika
import redis

try:
    import simplejson as json
except ImportError:
    import json


class Redis(redis.StrictRedis):
    host = 'localhost'

    def __init__(self):
        super(Redis, self).__init__(redis.StrictRedis(self.host))

    @classmethod
    def setup_hostname(cls, hostname):
        cls.host = hostname

    def set_task(self, id):
        self.set(id, -1)

    def cancel_task(self, id):
        self.set(id, 1000)

    def update_task(self, id, progress_delta=1):
        assert (progress_delta <= 100)
        return self.incrby(id, progress_delta)

    def check_task(self, id):
        progress = self.get(id)
        if progress is None:
            status = 'Task canceled'
        elif progress < 0:
            status = 'Enqueued'
        elif progress <= 100:
            status = 'Processing %d' % progress
        elif progress < 1000:
            status = 'Processing complete'
        else:
            status = 'Task canceled'
        return status


class RabbitMQ(pika.BlockingConnection):
    host = 'localhost'

    def __init__(self):
        self.consumer_callback = lambda x: ''
        super(RabbitMQ, self).__init__(pika.ConnectionParameters(self.host))

    @classmethod
    def setup_hostname(cls, hostname):
        cls.host = hostname

    def post_task(self, id):
        ch = self.channel()
        ch.queue_declare(queue='work')
        ch.basic_publish(
            exchange='',
            routing_key='work',
            body='{"id": "%s"}' % id,
            properties=pika.BasicProperties(
                delivery_mode=2,
            )
        )

    def consume_cb(self, channel, method, properties, body):
        task = json.loads(body)
        self.consumer_callback(task['id'])
        channel.basic_ack(delivery_tag=method.delivery_tag)

    def consume_jobs(self, callback):
        self.consumer_callback = callback

        ch = self.channel()
        ch.queue_declare(queue='work')
        ch.basic_qos(prefetch_count=1)
        ch.basic_consume(self.consume_cb, queue='work', no_ack=False)
        ch.start_consuming()


def parse_args():
    parser = argparse.ArgumentParser(description='Frontend of worker')
    parser.add_argument('redis', help='Redis hostname', default='localhost')
    parser.add_argument('rabbitmq', help='Rabbitmq hostname',
                        default='localhost')
    args = parser.parse_args()
    RabbitMQ.setup_hostname(args.rabbitmq)
    Redis.setup_hostname(args.redis)
