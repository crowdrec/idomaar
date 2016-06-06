# coding: utf-8

# In[85]:

import sys,json
from pyspark import SparkContext, SparkConf

conf = SparkConf()
sc = SparkContext(conf=conf)

inputFile = sys.argv[1]
if sys.argv[1] == '--help':
    print '''spark-submit eval.py recommendationFile outputFile configuration.json
        example configuration.json: [{"mode": "recall@N", "Nlist": [1, 2, 5, 10]}, {"mode": "CTR"}, {"mode": "avg_precision"},
        {"mode": "avg_precision@N", "Nlist": [1, 2, 5, 10]}]
        Already implemented: recall@N, avg_precision, avg_precision@N
    '''
     

outputFile = sys.argv[2]
confFile = sys.argv[3]


print "Reading from:",inputFile,"\nWriting in:",outputFile
try:
    configurations = sc.textFile(confFile).map(lambda x: json.loads(x)).first()
    print "Configuration file loaded!",configurations
except Exception:
    print "Configuration must be a json, loading default properties (recall@N with N in [1,2,5,10])"
    configurations = []
    configurations.append({'mode':'recall@N','Nlist':[1,2,5,10]})
    
def evalRecall(x,NList=[1,2,5,10]):
            GTList = set([k['object']['id'] for k in x['GT']['expected']['evidences']])
            res = {}
            for N in NList:
                recList = set([k['id'] for k in x['rec'] if int(k['rank']) <= N ])
                if N == -1:
                    recList = set([k['id'] for k in x['rec']])
                    N = 'hits'
                  
                res[N] = len(GTList & recList)
            res['GtLength'] = len(GTList)
            res['RecLength'] = len(set([k['id'] for k in x['rec']]))
            return res


def testAndTry(x):
    try: 
        return True,json.loads(x[3]),json.loads(x[7])
    except Exception:
        return False,x,len(x)        


# In[114]:

preDataRDD = sc.textFile(inputFile).map(lambda x: x.split("\t")).filter(lambda x: x[0] != "EOF")        .map(lambda x: (testAndTry(x))).persist()
print "Lines with issue(s)",preDataRDD.filter(lambda x: x[0] == False).count()
print "Lines correctly loaded",preDataRDD.filter(lambda x: x[0] == True).count()
dataRDD = preDataRDD.filter(lambda x: x[0] == True)                .map(lambda x: {'GT':x[1],'rec':x[2]}).persist()

res = {'metrics':{}}
for pos,configuration in enumerate(configurations):
    try:
        print "\nMode:",configuration['mode']
        if configuration['mode'] == 'recall@N':
            NList = configuration['Nlist']
            res['metrics']['recall@N'] = {}
            computedHits = dataRDD.map(lambda x: evalRecall(x,NList=NList)).persist()
            tot_GT = float(computedHits.map(lambda x: x['GtLength']).sum())
            print "Number of total elements in the GT:",int(tot_GT)

            for N in NList:
                score = computedHits.map(lambda x: x[N]).sum()/tot_GT
                print "Recall@"+str(N)+":",score
                res['metrics']['recall@N']['recall@'+str(N)] = score

            
                
        elif configuration['mode'] == 'avg_precision':
                computedHits = dataRDD.map(lambda x: evalRecall(x,[-1])).persist()
                tot_Rec = float(computedHits.map(lambda x: x['RecLength']).sum())
                tot_Hit = computedHits.map(lambda x: x['hits']).sum()
                print "Average Precision:", tot_Hit/tot_Rec
                res['metrics']['avg_precision'] = tot_Hit/tot_Rec
                
                
        elif configuration['mode'] == 'avg_precision@N':
            computedHits = dataRDD.map(lambda x: evalRecall(x,NList=NList)).persist()
            NList = configuration['Nlist'] 
            res['metrics']['avg_precision@N'] = {}
            base_num_rec = float(dataRDD.count())
            for N in NList:
                num_rec = N * base_num_rec
                score = computedHits.map(lambda x: x[N]).sum()/num_rec
                print "Average Precision@"+str(N)+":",score
                res['metrics']['avg_precision@N']['avg_precision@'+str(N)] = score
            
            

        else: 
            print "Sorry, noone has implemented",configuration['mode'],"evaluation method."
            print "Currently you can use 'recall@N', 'avg_precision'."
    except Exception:
        print "The",str(pos)+"-th configuration of your json has some issue."
try:
    if "s3" not in outputFile:
        with open(outputFile,'a') as f: f.write(json.dumps(res)+"\n")
    else:
        sc.parallelize(res).map(lambda x: json.dumps(x)).saveAsTextFile(outputFile)
except Exception:
    print "Some issue when trying to write the res file!!"


# In[22]:

# DEBUG ONLY

# import json
# execfile("/opt/util.py")
# inputFile = '/tmp/test_data'
# outputFile = '/tmp/outTest'
# configurations = [{"mode": "recall@N", "Nlist": [1, 2, 5, 10]}, {"mode": "CTR"}, {"mode": "avg_precision"},
#         {"mode": "avg_precision@N", "Nlist": [1, 2, 5, 10]}]
# print configurations

# def evalRecall(x,NList=[1,2,5,10]):
#             GTList = set([k['object']['id'] for k in x['GT']['expected']['evidences']])
#             res = {}
#             for N in NList:
#                 recList = set([k['id'] for k in x['rec'] if int(k['rank']) <= N ])
#                 if N == -1:
#                     recList = set([k['id'] for k in x['rec']])
#                     N = 'hits'
                  
#                 res[N] = len(GTList & recList)
#             res['GtLength'] = len(GTList)
#             res['RecLength'] = len(set([k['id'] for k in x['rec']]))
#             return res
# def testAndTry(x):
#     try: 
#         return True,json.loads(x[3]),json.loads(x[7])
#     except Exception:
#         return False,x,len(x)     

# preDataRDD = sc.textFile(inputFile).map(lambda x: x.split("\t")).filter(lambda x: x[0] != "EOF")\
#         .map(lambda x: (testAndTry(x))).persist()
# print "Lines with error(s)",preDataRDD.filter(lambda x: x[0] == False).count()
# print "Lines without error(s)",preDataRDD.filter(lambda x: x[0] == True).count()
# dataRDD = preDataRDD.filter(lambda x: x[0] == True)\
#                 .map(lambda x: {'GT':x[1],'rec':x[2]}).persist()