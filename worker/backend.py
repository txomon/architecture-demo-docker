from __future__ import absolute_import

import logging
import random
import time

import pika.exceptions

from worker.utils import TaskScheduler, configure_logging

logger = logging.getLogger()


def worker_cb(job_id):
    logger.info('Received task id %s', job_id)
    r = TaskScheduler()
    for t in range(100):
        status = r.update_task(job_id, random.randint(0, 10))
        logger.debug('Processing task id %s, total work %d', job_id, status)
        if status >= 1000:
            logger.debug('Task %s cancelled', job_id)
            break
        if status > 100:
            logger.debug('Task %s completed', job_id)
            break
        time.sleep(1)


def main():
    configure_logging()
    while True:
        try:
            rb = TaskScheduler()
            logger.info('Worker initialized, waiting for jobs')
            rb.consume_jobs(worker_cb)
        except pika.exceptions.ConnectionClosed:
            logger.warning('RabbitMQ not present, retrying')
            time.sleep(1)
            continue


if __name__ == '__main__':
    main()
