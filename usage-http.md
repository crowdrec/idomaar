# Idomaar HTTP Interface Usage

## Introduction
This template aims to make it easy to evaluate recommendation algorithms using a simple HTTP REST interface.

## Installation
Follow the steps in **Installation** section of [usage.md](usage.md) for basic installation instructions.

## Using the HTTP template
To let Idomaar evaluate your own recommendation algorithm using HTTP as transport protocol between the orchestrator and the computing environment, you have to let the server know how to fetch recommendations from your algorithm.

To do so, open file `computingenvironments\01.linux\01.centos\01.mahout\algorithms\02.http\idomaar-http-server.py` and edit the body of `recommend()` method (this is just an example):

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

    # Each recommendation is a dict item of 'rec' list inside 'resp' dict and it is formed
    # by {id, nextItemId, nextItemScore}. Response *must* follow this structure to be readable
    # by the evaluator
    for i in range(len(algo_resp)):
        resp['rec'].append({"id": int(algo_resp[i][0]), "rating": float(algo_resp[i][1]), "rank": i+1})
    
    return app.make_response(json.dumps(resp))
```

Note that the response sent by the server *must* follow the structure described in the above sample source code.

After you have properly edited this file, you can launch `idomaar-demo.sh` (or `idomaar-demo.bat` if you are using Windows) to start the evaluation process.