from flask import Flask, request

import time
import json
import logging
from logging.handlers import RotatingFileHandler

app = Flask(__name__)

@app.route('/')
def index():
    return 'Index'

@app.route('/HELLO', methods=['POST'])
def hello():
    return 'READY'

@app.route('/TRAIN', methods=['POST'])
def train():
    # The template skips this phase; replace this code if you want Idomaar to control training of your model
    time.sleep(1)
    return 'OK\nhttp://192.168.22.100:5001'

@app.route('/TEST', methods=['POST'])
def test():
    return 'OK'

@app.route('/STOP', methods=['POST'])
def stop():
    return 'OK'

@app.route('/', methods=['POST'])
def recommend():

    # Read request data from request.form.getlist('received-data') where 'received-data' is a string identifying the name of the property sent by the client.
    # See Flask documentation for further details about getlist() method.

    # Interface with your recommender algorithm and build your response

    resp = {}

    # Add properties to resp object to add recommendations

    return app.make_response(json.dumps(resp))

if __name__ == '__main__':
    handler = RotatingFileHandler('http_flask_server.log', maxBytes=10000, backupCount=1)
    handler.setLevel(logging.INFO)
    app.logger.addHandler(handler)

    app.run(host='0.0.0.0', port=5000)
