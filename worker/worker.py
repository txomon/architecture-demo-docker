from __future__ import absolute_import

import random
import time

from . import utils


def worker_cb(job_id):
    r = utils.Redis()
    for t in range(100):
        status = r.update_task(job_id, random.randint % 10)
        if status > 100:
            break
        if status >= 1000:
            break
        time.sleep(1)


def main():
    utils.parse_args()
    rb = utils.RabbitMQ()
    rb.consume_jobs(worker_cb)


if __name__ == '__main__':
    main()
