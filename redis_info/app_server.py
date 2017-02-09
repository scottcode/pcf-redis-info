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


@app.route('/redis_slowlog_len', methods=['GET'])
def redis_slowlog_len():
    request_time = time.strftime('%c (%z)', time.localtime())
    slowlog_len = r.slowlog_len()
    return jsonify({
        'time': request_time,
        'slowlog_len': slowlog_len
    })


@app.route('/redis_slowlog_get', methods=['GET'])
def redis_slowlog_get():
    request_time = time.strftime('%c (%z)', time.localtime())
    n = request.args.get('n')
    if n is not None:
        try:
            n = int(n)
        except (TypeError, ValueError):
            n = None
    slowlog_list = r.slowlog_get(n)
    return jsonify({
        'time': request_time,
        'slowlog_list': slowlog_list
    })


@app.route('/redis_client_list', methods=['GET'])
def redis_client_list():
    request_time = time.strftime('%c (%z)', time.localtime())
    client_list = r.client_list()
    return jsonify({
        'time': request_time,
        'client_list': client_list
    })


def serve_forever():
    """Start app server"""
    if os.environ.get('VCAP_SERVICES') is None:  # running locally
        PORT = 5001
        app.debug = True
    else:                                       # running on CF
        PORT = int(os.getenv("PORT"))
    http_server = WSGIServer(('0.0.0.0', PORT), app)
    http_server.serve_forever()


if __name__ == '__main__':
    serve_forever()
