import  zmq
import  os
from    enum import Enum
import  subprocess


class OrchestratorState(Enum):
    ready = 1
    reading_input = 2
    training = 3
    recommending = 4

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def log_info(msg):
    print bcolors.OKBLUE + msg + bcolors.ENDC

def log_error(msg):
    print bcolors.FAIL + msg + bcolors.ENDC

def log_warning(msg):
    print bcolors.WARNING + msg + bcolors.ENDC


class Orchestrator(object):
    def __init__(self, port=2760):
        self._context = zmq.Context()
        self._socket = self._context.socket(zmq.REP)
        self._socket.bind("tcp://*:%s" % port)
        self._state = OrchestratorState.ready

        self._training_uri = None
        self._test_uri = None
        self._computing_env = None
        self._algorithm = None

    @property
    def training_uri(self):
        return self._training_uri

    @training_uri.setter
    def training_uri(self, value):
        self._training_uri = value

    @property
    def test_uri(self):
        return self._test_uri

    @test_uri.setter
    def test_uri(self, value):
        self._test_uri = value

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
        log_info("DO: starting data stream")

        cmd = ['vagrant', 'up']
        env_vars = os.environ

        ret = subprocess.call(cmd, env=env_vars, cwd=self.datastreammanager)
        return ret


    def start_vm(self):
        if self.computing_env is None:
            log_error("computing env not set!")
            return

        log_info("DO: starting Computing environment")

        cmd = ['vagrant', 'up']
        env_vars = os.environ

        ret = subprocess.call(cmd, env=env_vars, cwd=self.computing_env)
        return ret


    def stop_vm(self):
        log_info("DO: Stopping computing environment")
        cmd = ['vagrant', 'halt']
        ret = subprocess.call(cmd, cwd=self.computing_env)
        return ret


    def run(self):
        if self.training_uri is None:
            log_error("Training dataset is not set!")
            return

        if self.test_uri is None:
            log_error("Test dataset is not set!")
            return

        log_warning("WAIT: waiting for machine to be ready")

        while True:
            log_warning("WAIT: waiting for new message in state ["+ self._state.name +"]"  )
            message = self._socket.recv_multipart()
            log_info("0MQ: received message: %s " % message)

            if message[0] == 'READY':
                log_info("INFO: machine started")

                # Tell the computing environment to start reading training data from the kafka queue
                # Pass to the orchestrator the zookeeper address and the name of the topics


                # TODO: zookeeper url has to be determined by vagrant from datastreammanager machine
                zookeeper = "192.168.22.5:2181"

                # THE FORMAT IS
                # MESSAGE, ZOOKEEPER URL, ENTITIES TOPIC, RELATIONS TOPIC
                msg = ['TRAIN', zookeeper, "data"]
                log_warning("WAIT: sending message "+ ''.join(msg) +" and wait for response")

                self._socket.send_multipart(msg)

                # start log4j agent on datastreammanager to read training data
                log_info("DO: starting data reader for training data uri=[" + orchestrator.training_uri + "]")

                cmd = [
                    "vagrant ssh -c 'sudo flume-ng agent --conf /vagrant/flume-config/log4j/training --name a1 --conf-file /vagrant/flume-config/config/idomaar-TO-kafka.conf -Didomaar.url=" + orchestrator.training_uri + " -Didomaar.sourceType=file'"]
                env_vars = os.environ
                ret = subprocess.call(cmd, env=env_vars, cwd=self.datastreammanager, shell=True)

                ## TODO CONFIGURE LOG IN ORDER TO TRACK ERRORS AND EXIT FROM ORCHESTRATOR
                ## TODO CONFIGURE FLUME IDOMAAR PLUGIN TO LOG IMPORTANT INFO AND LOG4J TO LOG ONLY ERROR FROM FLUME CLASS

                self._state = OrchestratorState.reading_input

            elif message[0] == 'OK':
                if self._state == OrchestratorState.reading_input:
                    log_info("INFO: recommender correctly trained")

                    # TODO DESTINATION FILE MUST BE PASSED FROM COMMAND LINE
                    # TODO RECOMMENDATION HOSTNAME MUST BE EXTRACTED FROM MESSAGES
                    recommendation_server_0mq = '192.168.22.100:5560'

                    log_warning("INFO: starting recommendation manager on data stream manager")
                    cmd = ["vagrant ssh -c 'sudo /vagrant/flume-config/startup/recommendation_manager-agent start " + recommendation_server_0mq +"'"]
                    env_vars = os.environ
                    ret = subprocess.call(cmd, env=env_vars, cwd=self.datastreammanager, shell=True)

                    log_warning("INFO: start sending test data to queue")
                    ## TODO CURRENTLY WE ARE TESTING ONLY "FILE" TYPE, WE NEED TO BE ABLE TO CONFIGURE A TEST OF TYPE STREAMING
                    cmd = [
                        "vagrant ssh -c 'sudo flume-ng agent --conf /vagrant/flume-config/log4j/test --name a1 --conf-file /vagrant/flume-config/config/idomaar-TO-kafka.conf -Didomaar.url=" + orchestrator.test_uri + " -Didomaar.sourceType=file'"]

                    ret = subprocess.call(cmd, env=env_vars, cwd=self.datastreammanager, shell=True)

                    ## TODO CONFIGURE LOG IN ORDER TO TRACK ERRORS AND EXIT FROM ORCHESTRATOR
                    ## TODO CONFIGURE FLUME IDOMAAR PLUGIN TO LOG IMPORTANT INFO AND LOG4J TO LOG ONLY ERROR FROM FLUME CLASS


                    msg = ['TEST']
                    log_warning("WAIT: sending message "+ ''.join(msg) +" and wait for response")

                    self._socket.send_multipart(msg)


                    self._state = OrchestratorState.recommending

                elif self._state == OrchestratorState.recommending:


                    log_info("INFO: recommendations correctly generated")

                    # TODO TRACK IF KAFKA RECOMMENDATION QUEUE IS EMPTY, OTHERWISE WAIT FOR DEQUEUE
                    log_warning("INFO: stop recommendation manager on data stream manager")
                    cmd = ["vagrant ssh -c 'sudo /vagrant/flume-config/startup/recommendation_manager-agent stop'"]
                    env_vars = os.environ
                    ret = subprocess.call(cmd, env=env_vars, cwd=self.datastreammanager, shell=True)


                    ## TODO RECEIVE SOME STATISTICS FROM THE COMPUTING ENVIRONMENT

                    break  

            elif message[0] == 'KO':

                if self._state == OrchestratorState.reading_input:
                    log_error("ERROR: machine failed to start. Process stopped.")
                elif self._state == OrchestratorState.training:
                    log_error("ERROR: some errors while training the recommender. \
                            Process stopped.")
                elif self._state == OrchestratorState.startRecommending:
                    log_error("ERROR: some errors while starting the recommender engine.")
                    print message
                elif self._state == OrchestratorState.recommending:
                    log_error("ERROR: some errors while generating recommendations.\
                            Process stopped.")
                else:
                    log_error("unknown error")

                break


            else:
                print ("unknown message type", message)
                continue

        print ("DO: stop")
        msg = ['STOP']
        self._socket.send_multipart(msg)

        log_warning("INFO: stopping recommendation manager on data stream manager")
        cmd = ["vagrant ssh -c 'sudo /vagrant/flume-config/startup/recommendation_manager-agent stop'"]
        env_vars = os.environ
        ret = subprocess.call(cmd, env=env_vars, cwd=self.datastreammanager, shell=True)


        self._socket.close()
        self._context.term()


if __name__ == '__main__':
    import sys

    basedir = os.path.abspath("../")
    computing_env_dir = os.path.join(basedir, "computingenvironments")

    orchestrator = Orchestrator()
    orchestrator.training_uri = sys.argv[2]
    orchestrator.test_uri = sys.argv[3]
    orchestrator.computing_env = os.path.join(computing_env_dir, sys.argv[1])
    orchestrator.datastreammanager = os.path.join(basedir, "datastreammanager")

    log_info("Idomaar base path: %s" % basedir)
    log_info("Training data URI: %s" % orchestrator.training_uri)
    log_info("Test data URI: %s" % orchestrator.test_uri)
    log_info("Computing environment path: %s" % orchestrator.computing_env)

    status = orchestrator.start_datastream()
    if status != 0:
        log_error("error starting data stream manager")
        sys.exit(1)

    # TODO: create/check data for validation

    status = orchestrator.start_vm()
    if status != 0:
        print ("error starting VM")
        sys.exit(1)

    orchestrator.run()

    # TODO: check if data stream channel is empty (http metrics)
    # TODO: test/evaluate the output

    # orchestrator.stop_vm()
    if status != 0:
        print ("error starting VM")
        sys.exit(1)

    print ("INFO: finished")
