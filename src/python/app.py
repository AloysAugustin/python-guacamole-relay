#!/usr/bin/env python

from gevent import monkey
monkey.patch_all()

from flask import Flask, app, render_template
from werkzeug.debug import DebuggedApplication
from geventwebsocket import WebSocketServer, Resource
from guacamole.websocket import GuacamoleWebsocketRelay


flask_app = Flask(__name__, template_folder='../web')
flask_app.debug = True

@flask_app.route('/')
def index():
    return render_template('index.html')

@flask_app.route('/all.min.js')
def js():
    return render_template('all.min.js')

@flask_app.route('/guacamole.css')
def css():
    return render_template('guacamole.css')


WebSocketServer(
    ('0.0.0.0', 8000),

    Resource([
        ('^/guac', ChatApplication),
        ('^/.*', DebuggedApplication(flask_app))
    ]),

    debug=True
).serve_forever()
