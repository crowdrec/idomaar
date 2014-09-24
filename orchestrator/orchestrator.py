
import zmq
import os
from enum import Enum
import subprocess


class OrchestratorState(Enum):
    ready = 1
    reading_input = 2
    training = 3
    recommending = 4


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

    def start_vm(self):
        if self.computing_env is None:
            print ("computing env not set!")
            return

        print ("DO: starting machine")

        cmd = ['vagrant', 'up']
        env_vars = os.environ
        env_vars['SHARED_ALGO'] = self.algorithm
        env_vars['SHARED_DATA'] = self.dataset
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
            message = self._socket.recv()
            print ("read message: %s " % message)

            if message == 'READY':
                print ("INFO: machine started")
                print ("DO: read input")

                entities = "/mnt/data/entities.dat"
                relations = "/mnt/data/relations.dat"
                msg = ['READ_INPUT', entities, relations]

                self._socket.send_multipart(msg)
                self._state = OrchestratorState.reading_input

            elif message == 'OK':
                if self._state == OrchestratorState.reading_input:
                    print ("INFO: input correctly read")
                    print ("DO: train")

                    msg = ['TRAIN']
                    self._socket.send_multipart(msg)
                    self._state = OrchestratorState.training

                elif self._state == OrchestratorState.training:
                    print ("INFO: recommender correctly trained")
                    print ("DO: recommend")

                    msg = ['RECOMMEND', '5', 'user:7', 'user:10', 'user:11', 'user:15', 'user:16', 'user:22', 'user:27', 'user:28'] # RECOMMEND RECLEN ENTITY1 ENTITY2...
                    self._socket.send_multipart(msg)
                    self._state = OrchestratorState.recommending

                elif self._state == OrchestratorState.recommending:
                    print ("INFO: recommendations correctly generated")
                    recoms = self._socket.recv_multipart()
                    print (recoms)

                    break

            elif message == 'KO':

                if self._state == OrchestratorState.reading_input:
                    print ("WARN: machine failed to start. Process stopped.")
                elif self._state == OrchestratorState.training:
                    print ("WARN: some errors while training the recommender. \
                        Process stopped.")
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
    datadir = os.path.join(basedir, "../datasets")
    computing_env_dir = os.path.join(basedir, "computingenvironments")

    print ("reference framework base path: %s" % basedir)
    print ("algorithm base path: %s" % algodir)
    print ("dataset path: %s" % datadir)
    print ("computing environment path: %s" % computing_env_dir)

    orchestrator = Orchestrator()
    orchestrator.algorithm = os.path.join(algodir, sys.argv[1])
    orchestrator.dataset = os.path.join(datadir, sys.argv[3])
    orchestrator.computing_env = os.path.join(computing_env_dir, sys.argv[2])

    status = orchestrator.start_vm()
    if status != 0:
        print ("error starting VM")
        sys.exit(1)

    orchestrator.run()

    # TODO: test/evaluate the output

    orchestrator.stop_vm()
    if status != 0:
        print ("error starting VM")
        sys.exit(1)

    print ("INFO: finished")
