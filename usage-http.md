# Python HTTP Interface Usage

## Introduction
This template aims to make it easy to evaluate recommendation algorithms using a simple HTTP REST interface written in Python (version 3.x).

## Installation
Follow the steps in **Installation** section of [usage.md](usage.md#installation) for basic installation instructions.

## Using the HTTP template
To let Idomaar evaluate your own recommendation algorithm using HTTP as transport protocol between the orchestrator and the computing environment, you have to let the server know how to fetch recommendations from your algorithm.

To do so, open file `computingenvironments/01.linux/01.centos/01.mahout/algorithms/02.http/idomaar-http-server.py` and edit the body of `recommend()` method (what follows is just an example):

```python
def recommend():
    recRequestProperties = json.loads(request.form.getlist('properties')[0])
    recRequestEntities = json.loads(request.form.getlist('entities')[0])

    sessionId = int(recRequestEntities['subject'].split(":")[1])
    previous = recRequestProperties['previouses'][0]
    prevItemId = int(previous['object']['id'])

    # predict_next_items() is a function defined somewhere in this file and contains
    # instructions to interact with your own algorithm; this is just an example!
    algo_resp = predict_next_items(algo_handler, sessionId, prevItemId, 20)

    resp = {}
    resp['GT'] = recRequestProperties
    resp['rec'] = []

    # Each recommendation is a dict item of 'rec' list inside 'resp' dict and it is formed by
    # {id, rating, rank}. Response *must* follow this structure to be readable by the evaluator
    for i in range(len(algo_resp)):
        resp['rec'].append({"id": int(algo_resp[i][0]), "rating": float(algo_resp[i][1]), "rank": i+1})
    
    return app.make_response(json.dumps(resp))
```

Note that the response `resp` sent by the server *must* follow the structure described in the above sample source code, that is, it must be a dictionary with keys `GT` and `rec`. `GT` contains the list of items for which you are asking recommendations, and `rec` contains a list of recommendations saved as dictionaries with keys `id` (the next item identifier, as returned by your algorithm), `rating` (the score associated with the current recommendation) and `rank` (it can be simply an ascending counter if recommendations are ordered by descending score).

This file implements all the methods required to interact with the orchestrator (see [Idomaar architecture](https://github.com/crowdrec/idomaar/wiki/Idomaar-architecture)); all requests are sent using POST method and the Python server listens to Idomaar's specific paths over POST method. In particular, the training phase is here skipped because you can train your model in a previous moment. If you want Idomaar to control your model training, you have to properly edit the `train()` method (see [Idomaar evaluation process](https://github.com/crowdrec/idomaar/wiki/Idomaar-evaluation-process) for details).

The full list of implemented methods (only POST requests are managed, since orchestrator sends POST requests) is:
* Request to path `/HELLO` is sent by the orchestrator to test if the computing environment is ready; when it is ready, the server answers with string `"READY"`
* Request to path `/TRAIN` causes starting your model training phase and the response is the string `"OK\n<ip_address:port>"` where `ip_address:port` is the recommendation endpoint
* Request to path `/TEST` tells the computing environment that the orchestrator is ready to serve recommendation requests; the server answers with the string `"OK"`
* Request to path `/` causes the start of the recommendation fetching process from the computing environment; the response is a string serialization of a JSON formatted object containing the recommendations
* Request to path `/STOP` causes the evaluation framework to terminate. Once the server is ready, it answers with the string `"OK"`

After you have finished editing `idomaar-http-server.py` according to your needs, you can launch `idomaar-demo.sh` (or `idomaar-demo.bat` if you are using Windows) to start the evaluation process.

## Troubleshooting
If the Python server doesn't automatically start when `idomaar-demo.sh` is executed, you need to start it from the computing environment by open a terminal in `computingenvironments\01.linux\01.centos\01.mahout` folder and then launching the following commands:

```sh
vagrant ssh

sudo service idomaar-http-server start
```

If it does not work, try launching

```sh
python3 /vagrant/algorithms/02.http/idommar-http-server.py
```

from the remote shell opened before.