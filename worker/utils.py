from __future__ import absolute_import

import logging
import pika
import redis

try:
    import simplejson as json
except ImportError:
    import json

logger = logging.getLogger()


class Redis(redis.StrictRedis):
    def __init__(self):
        super(Redis, self).__init__('redis')

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


class RabbitMQ(pika.BlockingConnection):
    def __init__(self):
        self.consumer_callback = lambda x: ''
        super(RabbitMQ, self).__init__(pika.ConnectionParameters('rabbitmq'))

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
        logger.debug("Received body '%s'", body)
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
