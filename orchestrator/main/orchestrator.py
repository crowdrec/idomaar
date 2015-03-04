from bsddb.dbtables import ExactCond
from setuptools.command.sdist import re_finder
import  zmq
import  os
from    enum import Enum
import  subprocess
import sys
import logging
import colorlog
import yaml
from orchestrator_exceptions import TimeoutException
from recommendation_manager import RecommendationManager
from util import timed_exec
from vagrant_executor import VagrantExecutor

logger = logging.getLogger("orchestrator")
computing_environment_logger = logging.getLogger("computing_environment")

class OrchestratorState(Enum):
    ready = 1
    reading_input = 2
    training = 3
    recommending = 4

class Orchestrator(object):
    def __init__(self, executor, datastreammanager, computing_env, training_uri, test_uri, port=2760):
        self.executor = executor
        self.datastreammanager = datastreammanager

        self.computing_env = computing_env
        self.training_uri = training_uri
        self.test_uri = test_uri

        if self.computing_env is None: raise Exception("Computing env not set!")
        if self.training_uri is None: raise Exception("Training dataset is not set!")
        if self.test_uri is None: raise Exception("Test dataset is not set!")

        logger.info("Training data URI: %s" % training_uri)
        logger.info("Test data URI: %s" % test_uri)
        logger.info("Computing environment path: %s" % computing_env)

        self._context = zmq.Context()
        self.comp_env_socket = self._context.socket(zmq.REQ)

        #self.comp_env_socket.bind("tcp://*:%s" % port)

        self._state = OrchestratorState.ready

        self.reco_manager_socket = zmq.Context().socket(zmq.REP)
        self.reco_manager_socket.bind('tcp://*:%s' % self.executor.orchestrator_port)

        # TODO Number of (concurrently running) recommendation managers should be configured externally, see issue #40
        self.num_concurrent_recommendation_managers = 1

        self.reco_managers_by_name = self.create_recommendation_managers(self.num_concurrent_recommendation_managers)

    def create_recommendation_managers(self, count):
        return {"RM" + str(i): RecommendationManager("RM" + str(i), self.executor) for i in range(count)}

    def start_computing_environment(self):
        logger.info("DO: starting Computing environment")
        return self.executor.start(working_dir=self.computing_env, subprocess_logger=computing_environment_logger)

    def read_yaml_config(self, file_name):
        with open(file_name, 'r') as input_file:
            return yaml.load(input_file)

    def send_train(self, zookeeper_hostport):
        """ Tell the computing environment to start reading training data from the kafka queue
            Instructs the flume agent on the datastreammanager vm to start streaming training data. Then sends a TRAIN message to the computing environment, and
            wait until training is complete."""

        logger.info("DO: starting data reader for training data uri=[" + str(self.training_uri) + "]")
        flume_command = 'flume-ng agent --conf /vagrant/flume-config/log4j/training --name a1 --conf-file /vagrant/flume-config/config/idomaar-TO-kafka.conf -Didomaar.url=' + self.training_uri + ' -Didomaar.sourceType=file'
        self.executor.run_on_data_stream_manager(flume_command)

        logger.info("Sending TRAIN message to computing environment and waiting for training to be ready ...")
        # Pass to the orchestrator the zookeeper address and the name of the topics
        # THE FORMAT IS
        # MESSAGE, ZOOKEEPER URL, ENTITIES TOPIC, RELATIONS TOPIC
        train_message = ['TRAIN', zookeeper_hostport, "data"]

        train_response, took_mins = timed_exec(lambda: self.response_from_comp_env(request=train_message))
        if train_response[0] == 'OK':
            logger.info("Training completed successfully, took {0} minutes.".format(took_mins))
            return train_response
        if train_response[0] == 'KO':
            raise Exception("ERROR: some errors while training the recommender.")
        else:
            raise Exception("Unexpected message received from computing environment." + str(train_response))


    def read_zookeeper_hostport(self):
        datastream_config = self.read_yaml_config(os.path.join(self.datastreammanager, "vagrant.yml"))
        datastream_ip_address = datastream_config['box']['ip_address']
        zookeeper_port = datastream_config['zookeeper']['port']
        zookeeper_hostport = "{host}:{port}".format(host=datastream_ip_address, port=zookeeper_port)
        return zookeeper_hostport

    def response_from_comp_env(self, request, timeout_millis=None):
        if type(request) is list: self.comp_env_socket.send_multipart(request)
        else: self.comp_env_socket.send(request)
        poller = zmq.Poller()
        poller.register(self.comp_env_socket, zmq.POLLIN) # POLLIN for recv, POLLOUT for send
        logger.info("Sending request {0} to computing environment.".format(request))
        logger.info("Waiting {time} for computing environment to answer ...".format(time=str(timeout_millis / 1000) + " secs" if timeout_millis else "indefinitely"))
        message = self.comp_env_socket.recv_multipart()
        if not message:
            self.comp_env_socket.close()
            raise TimeoutException("No answer from computing environment, probable timeout.")
        logger.info("Response from computing environment " + str(message))
        return message


    def connect_to_comp_env(self):
        computing_environment_address = "tcp://192.168.22.100:2760"
        computing_environment_startup_secs = 20

        self.comp_env_socket.connect(computing_environment_address)
        logger.info("Connected to " + computing_environment_address)
        logger.info("Waiting at most {secs} secs for computing environment to get ready ...".format(secs=computing_environment_startup_secs))
        try:
            message = self.response_from_comp_env(request="HELLO", timeout_millis=computing_environment_startup_secs*1000)
        except Exception:
            raise Exception("No answer from computing environment, probable timeout. Computing environment failed or didn't start in {secs} seconds.".format(secs=computing_environment_startup_secs))
        if message[0] != 'READY':
            raise Exception("Computing environment send message {0}, which is not READY.".format(message))

    def run(self):
        zookeeper_hostport = self.read_zookeeper_hostport()

        self.executor.start_datastream()
        self.executor.configure_datastream(self.num_concurrent_recommendation_managers, zookeeper_hostport)
        self.start_computing_environment()
        self.connect_to_comp_env()

        logger.info("Successfully connected to computing environment, start feeding train data.")

        train_response = self.send_train(zookeeper_hostport=zookeeper_hostport)

        # TODO DESTINATION FILE MUST BE PASSED FROM COMMAND LINE
        for reco_manager in self.reco_managers_by_name.itervalues():
            reco_manager.start()

        ## TODO CURRENTLY WE ARE TESTING ONLY "FILE" TYPE, WE NEED TO BE ABLE TO CONFIGURE A TEST OF TYPE STREAMING
        logger.info("Start sending test data to queue")

        test_data_feed_command = "flume-ng agent --conf /vagrant/flume-config/log4j/test --name a1 --conf-file /vagrant/flume-config/config/idomaar-TO-kafka.conf -Didomaar.url=" + orchestrator.test_uri + " -Didomaar.sourceType=file"
        self.executor.run_on_data_stream_manager(test_data_feed_command)

        ## TODO CONFIGURE LOG IN ORDER TO TRACK ERRORS AND EXIT FROM ORCHESTRATOR
        ## TODO CONFIGURE FLUME IDOMAAR PLUGIN TO LOG IMPORTANT INFO AND LOG4J TO LOG ONLY ERROR FROM FLUME CLASS

        test_message = ['TEST']
        logger.warn("WAIT: sending message "+ ''.join(test_message) +" and wait for response")

        self.response_from_comp_env(request=test_message)

        self._state = OrchestratorState.recommending

        logger.info("INFO: recommendations correctly generated, waiting for finished message from recommendation manager agents")

        reco_manager_message = self.reco_manager_socket.recv_multipart()
        logger.info("Message from recommendation manager: %s " % reco_manager_message)
        if reco_manager_message[0] == "FINISHED":
            reco_manager_name = reco_manager_message[1] if len(reco_manager_message) > 1 else ""
            reco_manager = self.reco_managers_by_name.get(reco_manager_name)
            if reco_manager is not None:
                logger.info("Recommendation manager " + reco_manager_name + "has finished processing recommendation queue, shutting all managers down.")
                for manager in self.reco_managers_by_name.itervalues(): reco_manager.stop()
            else:
                logger.error("Received FINISHED message from a recommendation manager named " + reco_manager_name + " but no record of this manager is found.")

        ## TODO RECEIVE SOME STATISTICS FROM THE COMPUTING ENVIRONMENT


        logger.info("DO: stop")
        msg = ['STOP']
        self.comp_env_socket.send_multipart(msg)

        self.comp_env_socket.close()
        self._context.term()

    def close(self):
        logger.info("Orchestrator closing...")
#        self.comp_env_socket.close()
        self._context.destroy()
        logger.info("Orchestrator shutdown.")


def setup_logging(logger_to_conf):
    logger_to_conf.setLevel("DEBUG")
    logger_to_conf.propagate = False
    handler = logging.StreamHandler(sys.stdout)

    formatter = colorlog.ColoredFormatter(
        "%(log_color)s%(levelname)-8s [%(name)s] %(message)s",
        datefmt=None,
        reset=True,
        log_colors={
            'DEBUG':    'blue',
            'INFO':     'blue',
            'WARNING':  'yellow',
            'ERROR':    'red',
            'CRITICAL': 'red',
            },
        secondary_log_colors={},
        style='%')

    handler.setFormatter(formatter)
    logger_to_conf.addHandler(handler)


if __name__ == '__main__':

    root_logger = logging.getLogger()
    setup_logging(root_logger)

    basedir = os.path.abspath("../../")
    computing_env_dir = os.path.join(basedir, "computingenvironments")

    # TODO RECOMMENDATION HOSTNAME MUST BE EXTRACTED FROM MESSAGES
    vagrant_executor = VagrantExecutor(reco_engine_hostport='192.168.22.100:5560', orchestrator_port=2761,
                                       datastream_manager_working_dir=os.path.join(basedir, "datastreammanager"), recommendation_timeout_millis=4000)

    orchestrator = Orchestrator(executor=vagrant_executor,
                                datastreammanager = os.path.join(basedir, "datastreammanager"),
                                computing_env = os.path.join(computing_env_dir, sys.argv[1]),
                                training_uri = sys.argv[2], test_uri = sys.argv[3])

    logger.info("Idomaar base path: %s" % basedir)

    try:
        orchestrator.run()
    except Exception:
        logger.exception("Exception occurred, hard shutdown.")
        os._exit(-1)

    # TODO: check if data stream channel is empty (http metrics)
    # TODO: test/evaluate the output

    #logger.info("DO: Stopping computing environment")
    #orchestrator.executor.stop(working_dir=orchestrator.computing_env, subprocess_logger=computing_environment_logger)

    logger.info("Finished.")
