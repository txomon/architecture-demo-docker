from __future__ import absolute_import

import logging

import pika

import redis

try:
    import simplejson as json
except ImportError:
    import json

logger = logging.getLogger()


class TaskScheduler(object):
    def __init__(self):
        self._redis = None
        self._rabbitmq = None
        self.consumer_callback = lambda x: ''

    def get_redis(self):
        if not self._redis:
            self._redis = redis.StrictRedis('redis')

        return self._redis

    redis = property(get_redis)

    def get_rabbitmq(self):
        if not self._rabbitmq:
            self._rabbitmq = pika.BlockingConnection(
                pika.ConnectionParameters('rabbitmq')
            )
        return self._rabbitmq

    rabbitmq = property(get_rabbitmq)

    def cancel_task(self, id):
        self.redis.setnx(id, 1000)

    def update_task(self, id, progress_delta=1):
        assert (progress_delta <= 100)
        return self.redis.incrby(id, progress_delta)

    def check_task(self, id):
        progress = self.redis.get(id)
        if progress is None:
            return 'Task cancelled'
        try:
            progress = int(progress)
        except:
            logger.exception('Error on progress to integer conversion')
            return 'Task cancelled'
        if progress < 0:
            return 'Enqueued'
        if progress <= 100:
            return 'Processing %d' % progress
        if progress < 1000:
            return 'Processing complete'
        return 'Task cancelled'

    def post_task(self, id):
        self.redis.set(id, -1)

        ch = self.rabbitmq.channel()
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
        if isinstance(body, bytes):
            body = body.decode()
        task = json.loads(body)
        self.consumer_callback(task['id'])
        channel.basic_ack(delivery_tag=method.delivery_tag)

    def consume_jobs(self, callback):
        self.consumer_callback = callback

        ch = self.rabbitmq.channel()
        ch.queue_declare(queue='work')
        ch.basic_qos(prefetch_count=1)
        ch.basic_consume(self.consume_cb, queue='work', no_ack=False)
        ch.start_consuming()


def configure_logging():
    asctime_format = "%Y%m%d_%I:%M:%S"
    log_format = "%(asctime)s:%(name)s:%(levelname)s:%(message)s"
    logging.basicConfig(
        level=logging.DEBUG,
        datefmt=asctime_format,
        format=log_format,
    )
    logging.getLogger('pika').setLevel(logging.WARN)
    logging.getLogger('cherrypy').setLevel(logging.WARN)
