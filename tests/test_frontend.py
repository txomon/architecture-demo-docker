try:
    from unittest import mock
except ImportError:
    import mock

import cherrypy

from worker.frontend import MyAPI, main
from worker.utils import TaskScheduler


@mock.patch('worker.frontend.TaskScheduler', spec=TaskScheduler)
def test_task_creation(ts):
    api = MyAPI()
    api._start()

    assert ts.call_count == 1
    assert ts.return_value.post_task.call_count == 1
    first_args = ts.return_value.post_task.call_args

    ts.reset_mock()
    api._start()
    assert ts.call_count == 1
    assert ts.return_value.post_task.call_count == 1
    second_args = ts.return_value.post_task.call_args

    assert first_args != second_args


@mock.patch('worker.frontend.TaskScheduler')
def test_task_check(ts):
    api = MyAPI()
    api._check('asdf')

    print(ts.mock_calls)
    assert ts.call_count == 1
    ts.return_value.check_task.assert_called_once_with('asdf')


def test_index_page():
    api = MyAPI()
    api._start = mock.Mock()
    api._check = mock.Mock()

    api.index()
    api._start.assert_called_once_with()

    api.index('asdf')
    api._check.assert_called_once_with('asdf')


@mock.patch('worker.frontend.TaskScheduler')
def test_cancel_page(ts):
    api = MyAPI()
    api.cancel('asdf')

    assert ts.call_count == 1
    ts.return_value.cancel_task.assert_called_once_with('asdf')


@mock.patch('worker.frontend.MyAPI', spec=MyAPI)
@mock.patch('worker.frontend.configure_logging')
@mock.patch('worker.frontend.cherrypy', spec=cherrypy)
def test_backend_main(cp_m, cl_m, ma_m):
    main()

    assert cl_m.call_count == 1
    assert ma_m.call_count == 1
    assert cp_m.quickstart.call_count == 1
    args, kwargs = cp_m.quickstart.call_args
    assert ma_m.return_value in args
