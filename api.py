import uuid

try:
    import simplejson as json
except ImportError:
    import json

import cherrypy
import pika
import redis


class MyAPI(self):
    @cherrypy.expose
    def index(self, id=None):
        if id:
            return self._check(id)
        else:
            return self._start()

    @cherrypy.expose
    def _start(self):
        id = str(uuid.uuid4())
        r = redis.StrictRedis(cherrypy.request.app.config['redis'])
        rabbitmq = pika.BlockingConnection(pika.ConnectionParameters(
            cherrypy.request.app.config['rabbitmq']
        ))
        ch = rabbitmq.channel()
        ch.queue_declare(queue='work')
        ch.basic_publish(exchange='',
                routing_key='work_queue',
                body=json.dumps
        r.set(id, -1)
        return '''<html>
        <body>
            <h1>Task created</h1>
            <a href="/?id=%s">Check task status.</a>
        </body>
    </html>''' % id


    @cherrypy.expose
    def _check(self, id):


def main():
    config = {
        '/': {'tools.gzip.on': True}
        'redis': args.redis,
        'rabbitmq': args.rabbitmq,
        }
    cherrypy.quickstart(MyAPI(), config=config)

if '__main__' == __name__:
    main()
