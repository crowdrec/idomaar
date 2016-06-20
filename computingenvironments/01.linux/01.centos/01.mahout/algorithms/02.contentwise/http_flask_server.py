from flask import Flask, request

import sys
sys.path.append('gru4rec')

import time
import boto3
import pickle
import gru4rec
import numpy as np
import pandas as pd

app = Flask(__name__)

# Loads the GRU (modify gru.pickle to gru1000.pickle)
def load_gru_from_s3():
    s3 = boto3.resource('s3')
    obj = s3.Bucket('contentwise-research').Object('gru.pickle').get()['Body'].read()
    return pickle.loads(obj)

# Loads the GRU from local fs
def load_gru_from_fs():
    with open('gru4rec/gru.pickle', 'rb') as f:
        return pickle.load(f)

# Predicts the next item given a trained GRU, a session and a list of items
def predict_next_item(gru, session_id, item_ids):
    sessions = [session_id] * len(item_ids)
    return gru.predict_next_batch(np.array(sessions), np.array(item_ids), None, len(item_ids)).sort_values([len(item_ids)-1], ascending=False).iloc[0].name

@app.route('/')
def index():
    return 'Index'

@app.route('/HELLO', methods=['POST'])
def hello():
    return 'READY'

@app.route('/TRAIN', methods=['POST'])
def train():
    time.sleep(1)
    return 'OK\nhttp://192.169.22.100:5000'

@app.route('/TEST', methods=['POST'])
def test():
    return 'OK'

@app.route('/RECOMMEND/<session>/<items>', methods=['POST'])
def recommend(session, items):
    gru = load_gru_from_fs()
    session_int = int(session)
    items_int = [int(x) for x in items.split(',')]
    rec = predict_next_item(gru, session_int, items_int)
    return 'OK\n' + str(rec)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)