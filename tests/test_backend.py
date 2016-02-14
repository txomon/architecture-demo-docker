import random
import time

try:
    from unittest import mock
except ImportError:
    import mock

import pika.exceptions

from worker.backend import main, worker_cb
from worker.utils import TaskScheduler


@mock.patch('worker.backend.random', spec=random)
@mock.patch('worker.backend.time', spec=time)
@mock.patch('worker.backend.TaskScheduler', spec=TaskScheduler)
def test_worker_cb(ts, time_m, random_m):
    random_m.randint.return_value = 8

    # Normal case
    update_task_mock = ts.return_value.update_task

    progress_status = [0, 39, 69, 112, 1233]
    update_task_mock.side_effect = lambda x, y: progress_status.pop(0)

    worker_cb('asdf')

    assert ts.call_count == 1
    assert progress_status == [1233]
    assert update_task_mock.call_count == 4
    update_task_mock.assert_called_with('asdf', 8)

    # Cancellation after once cycle
    ts.reset_mock()
    update_task_mock = ts.return_value.update_task

    progress_status = [0, 1233, 8]
    update_task_mock.side_effect = lambda x, y: progress_status.pop(0)

    worker_cb('asdf')

    assert ts.call_count == 1
    assert progress_status == [8]
    assert update_task_mock.call_count == 2
    update_task_mock.assert_called_with('asdf', 8)

    # Cancelation from the beginning
    ts.reset_mock()
    update_task_mock = ts.return_value.update_task

    progress_status = [1233, 8]
    update_task_mock = ts.return_value.update_task
    update_task_mock.side_effect = lambda x, y: progress_status.pop(0)

    worker_cb('asdf')

    assert ts.call_count == 1
    assert progress_status == [8]
    update_task_mock.assert_called_once_with('asdf', 8)


@mock.patch('worker.backend.configure_logging')
@mock.patch('worker.backend.time', spec=time)
@mock.patch('worker.backend.TaskScheduler', spec=TaskScheduler)
def test_backend_main(ts, time_m, cl_m):
    cj_m = ts.return_value.consume_jobs
    cj_m.side_effect = pika.exceptions.ConnectionClosed

    class SleepFunc(object):
        called = False

        def sleep_func(self, arg):
            if not self.called:
                self.called = True
                return
            else:
                raise BufferError()

    time_m.sleep.side_effect = SleepFunc().sleep_func

    try:
        main()
    except BufferError:
        pass

    assert cl_m.call_count == 1
    assert ts.call_count == 2
    cj_m.assert_called_with(worker_cb)
