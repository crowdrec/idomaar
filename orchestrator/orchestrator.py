
import zmq
import os
from enum import Enum
import subprocess


class OrchestratorState(Enum):
    ready = 1
    reading_input = 2
    training = 3
    startRecommending = 4
    recommending = 5


class Orchestrator(object):
    def __init__(self, port=2760):
        self._context = zmq.Context()
        self._socket = self._context.socket(zmq.REP)
        self._socket.bind("tcp://*:%s" % port)
        self._state = OrchestratorState.ready

        self._dataset = None
        self._computing_env = None
        self._algorithm = None

    @property
    def dataset(self):
        return self._dataset

    @dataset.setter
    def dataset(self, value):
        self._dataset = value

    @property
    def computing_env(self):
        return self._computing_env

    @computing_env.setter
    def computing_env(self, value):
        self._computing_env = value

    @property
    def algorithm(self):
        return self._algorithm

    @algorithm.setter
    def algorithm(self, value):
        self._algorithm = value

    def start_datastream(self):

        print ("DO: starting data stream")

        cmd = ['vagrant', 'up']
        env_vars = os.environ

        ret = subprocess.call(cmd, env=env_vars, cwd=self.datastreammanager)
        return ret

    def start_vm(self):
        if self.computing_env is None:
            print ("computing env not set!")
            return

        print ("DO: starting machine")

        cmd = ['vagrant', 'up']
        env_vars = os.environ

        ret = subprocess.call(cmd, env=env_vars, cwd=self.computing_env)
        return ret

    def stop_vm(self):
        print ("DO: Stopping computing environment")
        cmd = ['vagrant', 'halt']
        ret = subprocess.call(cmd, cwd=self.computing_env)
        return ret

    def run(self):
        if self.dataset is None:
            print("recommendation dataset is not set!")
            return

        print ("STATUS: waiting for machine to be ready")
        while True:
            print ("reading message")
            message = self._socket.recv_multipart()
            print ("read message: %s " % message)

            if message[0] == 'READY':
                print ("INFO: machine started")
                print ("DO: read input")

                # Tell the computing environment to start reading training data from the kafka queue
                # Pass to the orchestrator the zookeeper address and the name of the topics

                # TODO THIS HAS TO BE PARAMETRIC
                cmd = ["vagrant ssh -c 'flume-ng agent --name a1 --conf-file /vagrant/config/idomaar-TO-kafka.conf -Didomaar.url=https://raw.githubusercontent.com/crowdrec/datasets/master/01.MovieTweetings/datasets/snapshots_10K/evaluation/training/data.dat -Didomaar.sourceType=file'"]
                env_vars = os.environ


                # TODO: zookeeper url has to be determined by vagrant from datastreammanager machine

                zookeeper = "192.168.22.5:2181"
                # THE FORMAT IS
                # MESSAGE, ZOOKEEPER URL, ENTITIES TOPIC, RELATIONS TOPIC
                msg = ['READ_INPUT', zookeeper, "data"]

                self._socket.send_multipart(msg)

                ## TODO MANAGE HOW TO CLOSE/TRACK EXIT CODE
                print "Starting FLUME training task"
                ret = subprocess.call(cmd, env=env_vars, cwd=self.datastreammanager, shell=True    )

                self._state = OrchestratorState.reading_input

            elif message[0] == 'OK':
                if self._state == OrchestratorState.reading_input:
                    print ("INFO: recommender correctly trained")
                    print ("DO: recommend")

               


                    msg = ['START_RECOMMEND']
                    self._socket.send_multipart(msg)
                    self._state = OrchestratorState.startRecommending

                elif self._state == OrchestratorState.startRecommending:
                    ## TODO START FLUME AGENT ON DATA STREAM MANAGER WITH DESTINATION TAKEN FROM 
                    ## ZEROMQ MESSAGE MESSAGE[1]

                    ## TODO: START FLUME AGENT THAT READ SOURCE DATASET AND SEND DATA TO KAFKA (STREAM AND RECOMMENDATION)
                    ## msg = ['RECOMMEND', '5', 'user:7', 'user:10', 'user:11', 'user:15', 'user:16', 'user:22', 'user:27', 'user:28'] # RECOMMEND RECLEN ENTITY1 ENTITY2...
                    # self._socket.send_multipart(msg)
                    # TODO THIS HAS TO BE PARAMETRIC

                    ## TODO IT HAS TO USE THE IP PARAMETERS 
                    print "received message"
                    print message[1]
                    cmd = "vagrant ssh -c 'flume-ng agent --name a1 --conf-file /vagrant/config/kafka_recommendations-TO-fs.conf -Didomaar.recommendation.hostname=tcp://192.168.0.42:5560'"
                    env_vars = os.environ

                    ## TODO MANAGE HOW TO CLOSE/TRACK EXIT CODE
                    print "Starting FLUME recommendation task"
                    #TODO UNCOMMENT IT AND MANAGE THE START/STOP WITH SYSTEM SERVICE
                    #ret = subprocess.Popen(cmd, env=env_vars, cwd=self.datastreammanager, shell=True)



                    cmd = "vagrant ssh -c 'flume-ng agent --name a1 --conf-file /vagrant/config/idomaar-TO-kafka.conf -Didomaar.url=https://raw.githubusercontent.com/crowdrec/datasets/master/01.MovieTweetings/datasets/snapshots_10K/evaluation/test/data.dat -Didomaar.sourceType=file'"
                    env_vars = os.environ

                    ## TODO MANAGE HOW TO CLOSE/TRACK EXIT CODE
                    print "Starting FLUME test task"
                    ret = subprocess.call(cmd, env=env_vars, cwd=self.datastreammanager, shell=True)


                    self._state = OrchestratorState.recommending

                elif self._state == OrchestratorState.recommending:
                    print ("INFO: recommendations correctly generated")
                    recoms = self._socket.recv_multipart()
                    print (recoms)

                    break

            elif message[0] == 'KO':

                if self._state == OrchestratorState.reading_input:
                    print ("WARN: machine failed to start. Process stopped.")
                elif self._state == OrchestratorState.training:
                    print ("WARN: some errors while training the recommender. \
                        Process stopped.")
                elif self._state == OrchestratorState.startRecommending:
                    print ("WARN: some errors while starting the recommender engine.")
                    print message
                elif self._state == OrchestratorState.recommending:
                    print ("WARN: some errors while generating recommendations.\
                        Process stopped.")
                else:
                    print ("unknown error")

                break

            else:
                print ("unknown message type", message)
                continue

        print ("DO: stop")
        msg = ['STOP']
        self._socket.send_multipart(msg)

        self._socket.close()
        self._context.term()

if __name__ == '__main__':
    import sys

    basedir = os.path.abspath("../")
    algodir = os.path.join(basedir, "algorithms")
    computing_env_dir = os.path.join(basedir, "computingenvironments")


    orchestrator = Orchestrator()
    orchestrator.dataset = sys.argv[2]
    orchestrator.computing_env = os.path.join(computing_env_dir, sys.argv[1])
    orchestrator.datastreammanager = os.path.join(basedir, "datastreammanager")

    print ("Idomaar base path: %s" % basedir)
    print ("Dataset URI: %s" % orchestrator.dataset)
    print ("Computing environment path: %s" % orchestrator.computing_env)

    status = orchestrator.start_datastream()
    if status != 0:
        print ("error starting data stream manager")
        sys.exit(1)

    # TODO: create/check data for validation

    status = orchestrator.start_vm()
    if status != 0:
        print ("error starting VM")
        sys.exit(1)

    orchestrator.run()

    # TODO: check if data stream channel is empty (http metrics)
    # TODO: test/evaluate the output

    #orchestrator.stop_vm()
    if status != 0:
        print ("error starting VM")
        sys.exit(1)

    print ("INFO: finished")
