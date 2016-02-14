from __future__ import absolute_import

import logging
import uuid

import cherrypy
from worker.utils import TaskScheduler, configure_logging

logger = logging.getLogger()


class MyAPI(object):
    @cherrypy.expose
    def index(self, id=None):
        if id:
            return self._check(id)
        else:
            return self._start()

    @cherrypy.expose
    def _start(self):
        id = str(uuid.uuid4())
        sched = TaskScheduler()
        sched.post_task(id)
        return '''<html>
        <body>
            <h1>Task created</h1>
            <p><a href="/?id=%s">Check task status.</a></p>
            <script> setTimeout(function() {
             location.href = "/?id=%s";
             }, 4000) </script>
        </body>
    </html>''' % (id, id)

    @cherrypy.expose
    def _check(self, id):
        r = TaskScheduler()
        status = r.check_task(id)

        return '''<html>
        <body>
            <h1>Task %s</h1>
            <p>%s</p>
            <p><a href="/cancel?id=%s">Cancel task</a></p>
            <script> setTimeout(function() {
            location.reload();
            }, 5000); </script>
        </body>
        </html>''' % (id, status, id)

    @cherrypy.expose
    def cancel(self, id):
        r = TaskScheduler()
        r.cancel_task(id)
        return '''<html><body><script>location.href =  "/?id=%s";</script>
        ''' % (id)


def main():
    configure_logging()
    config = {
        '/': {'tools.gzip.on': True},
        'global': {'server.socket_host': "0.0.0.0"}
    }
    cherrypy.quickstart(MyAPI(), config=config)


if '__main__' == __name__:
    main()
