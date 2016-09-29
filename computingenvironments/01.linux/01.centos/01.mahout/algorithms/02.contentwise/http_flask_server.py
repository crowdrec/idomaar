from flask import Flask, request

import sys
sys.path.append('/vagrant/algorithms/02.contentwise/gru4rec')

import time
import boto3
import json
import pickle
import logging
from logging.handlers import RotatingFileHandler
import gru4rec
import numpy as np
import pandas as pd

app = Flask(__name__)

# Loads the GRU from Amazon S3
def load_gru_from_s3():
    s3 = boto3.resource('s3')
    obj = s3.Bucket('contentwise-research').Object('gru.pickle').get()['Body'].read()
    return pickle.loads(obj)

# Loads the GRU from local file system
def load_gru_from_fs():
    with open('/vagrant/algorithms/02.contentwise/gru4rec/gru_1000_crossentropy.pickle', 'rb') as f:
        return pickle.load(f)

# Predicts the next item given a trained GRU, a session and a list of items
def predict_next_items(gru, session_id, item_ids, n_recs):
    sessions = [session_id] * len(item_ids)

    df = gru.predict_next_batch(np.array(sessions, dtype=np.int32), np.array(item_ids, dtype=np.int32), None, len(item_ids)).sort_values([len(item_ids)-1], ascending=False)[:n_recs]

    items_and_scores = []

    for r in df.itertuples():
        items_and_scores.append((r[0], r[1]))

    return items_and_scores

@app.route('/')
def index():
    return 'Index'

@app.route('/HELLO', methods=['POST'])
def hello():
    return 'READY'

@app.route('/TRAIN', methods=['POST'])
def train():
    app.logger.error(request.form)
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

    #ImmutableMultiDict([('type', 'recommendation'), ('properties', '{"reclen":20, "event_type": "recommendation_request", "context":{"simple":{}}, "expected": {"evidences": [{"evidence": {"type": "click"}, "subject": {"type": "session", "id": 11255568}, "object": {"type": "item", "id": "214857030"}}]}, "previouses": [{"evidence": {"type": "click"}, "subject": {"type": "session", "id": 11255568}, "object": {"type": "item", "id": "214696432"}}]}'), ('entities', '{"subject":"session:11255568"}')])
    recRequestProperties = json.loads(request.form.getlist('properties')[0])
    recRequestEntities = json.loads(request.form.getlist('entities')[0])

    app.logger.error("recRequestProperties")
    app.logger.error(recRequestProperties)

    sessionId = int(recRequestEntities['subject'].split(":")[1])
    previous = recRequestProperties['previouses'][0]
    prevItemId = int(previous['object']['id'])

    gru_resp = predict_next_items(gru, sessionId, [prevItemId], 20)

    resp = {}
    resp['GT'] = recRequestProperties
    resp['rec'] = []

    for i in range(len(gru_resp)):
        #                           nextItemId                  nextItemScore
        resp['rec'].append({"id": int(gru_resp[i][0]), "rating": float(gru_resp[i][1]), "rank": i+1})


    return app.make_response(json.dumps(resp))

if __name__ == '__main__':
    handler = RotatingFileHandler('gru.log', maxBytes=10000, backupCount=1)
    handler.setLevel(logging.INFO)
    app.logger.addHandler(handler)

    global gru
    gru = load_gru_from_fs()

    app.run(host='0.0.0.0', port=5000)
