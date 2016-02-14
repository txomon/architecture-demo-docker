from __future__ import absolute_import

import logging
import uuid

import cherrypy
from worker import utils

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
        r = utils.Redis()
        rabbitmq = utils.RabbitMQ()
        r.set_task(id)
        rabbitmq.post_task(id)
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
        r = utils.Redis()
        status = r.check_task(id)

        return '''<html>
        <body>
            <h1>Task %s</h1>
            <p>%s</p>
            <script> setTimeout(function() {
            location.reload();
            }, 1000); </script>
        </body>
        </html>''' % (id, status)

    @cherrypy.expose
    def cancel(self, id):
        r = utils.Redis()
        r.cancel_task(id)
        return '''
        '''


def main():
    logging.basicConfig(level=logging.DEBUG)
    config = {
        '/': {'tools.gzip.on': True},
        'global': {'server.socket_host': "0.0.0.0"}
    }
    cherrypy.quickstart(MyAPI(), config=config)


if '__main__' == __name__:
    main()
