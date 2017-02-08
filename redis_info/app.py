"""
twitter nlp
~~~~~~~~~~~

Serves the web application and sends tweets and tweet data using Server Side Events (SSE)

"""

import os
import time

import redis
from flask import Flask, request, jsonify
from gevent import monkey, socket
from gevent.pywsgi import WSGIServer

from connection import connect_redis_db

monkey.patch_all()

app = Flask(__name__)
redis.connection.socket = socket

# connect to redis for storing logging info
r = connect_redis_db()


@app.route('/redis_info', methods=['GET'])
def redis_info():
    return jsonify({
        "info_time": time.strftime('%c', time.gmtime()),
        "redis_info": r.info()
    })


@app.route('/redis_list_len', methods=['GET'])
def redis_list_len():
    listname = request.args.get('list')
    if listname is not None:
        return jsonify({
            "listname": listname,
            "length": r.llen(listname)
        })
    else:
        return jsonify({
            "listname": "",
            "length": 0
        })


def serve():
    """Start app server"""
    if os.environ.get('VCAP_SERVICES') is None:  # running locally
        PORT = 5001
        app.debug = True
    else:                                       # running on CF
        PORT = int(os.getenv("PORT"))
    http_server = WSGIServer(('0.0.0.0', PORT), app)
    http_server.serve_forever()


if __name__ == '__main__':
    serve()
