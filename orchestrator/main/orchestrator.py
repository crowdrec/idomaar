import  zmq
import  os
from    enum import Enum
import  subprocess
import sys
import logging
import colorlog
from recommendation_manager import RecommendationManager
from vagrant_executor import VagrantExecutor

logger = logging.getLogger("orchestrator")
computing_environment_logger = logging.getLogger("computing_environment")

class OrchestratorState(Enum):
    ready = 1
    reading_input = 2
    training = 3
    recommending = 4

class Orchestrator(object):
    def __init__(self, executor, port=2760):
        self._context = zmq.Context()
        self.executor = executor
        self._socket = self._context.socket(zmq.REP)
        self._socket.bind("tcp://*:%s" % port)
        self._state = OrchestratorState.ready

        self.reco_manager_socket = zmq.Context().socket(zmq.REP)
        self.reco_manager_socket.bind('tcp://*:%s' % self.executor.orchestrator_port)

        # TODO Number of (concurrently running) recommendation managers should be configured externally, see issue #40
        self.num_concurrent_recommendation_managers = 10

        self.reco_managers_by_name = self.create_recommendation_managers(self.num_concurrent_recommendation_managers)

        self._training_uri = None
        self._test_uri = None
        self._computing_env = None
        self._algorithm = None

    def create_recommendation_managers(self, count):
        return {"RM" + str(i): RecommendationManager("RM" + str(i), self.executor) for i in range(count)}

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

    def start_vm(self):
        if self.computing_env is None:
            logger.error("computing env not set!")
            return
        logger.info("DO: starting Computing environment")
        return self.executor.start(working_dir=self.computing_env, subprocess_logger=computing_environment_logger)

    def send_train(self):
        """Sends a TRAIN message to the computing environment, then instructs the flume agent on the datastreammanager vm to start streaming training data"""
        # TODO: zookeeper url has to be determined by vagrant from datastreammanager machine
        zookeeper = "192.168.22.5:2181"

        # Pass to the orchestrator the zookeeper address and the name of the topics
        # THE FORMAT IS
        # MESSAGE, ZOOKEEPER URL, ENTITIES TOPIC, RELATIONS TOPIC
        msg = ['TRAIN', zookeeper, "data"]
        logger.warning("WAIT: sending message ["+ ', '.join(msg) +"] and wait for response")

        self._socket.send_multipart(msg)

        # start log4j agent on datastreammanager to read training data
        logger.info("DO: starting data reader for training data uri=[" + str(self.training_uri) + "]")

        flume_command = 'flume-ng agent --conf /vagrant/flume-config/log4j/training --name a1 --conf-file /vagrant/flume-config/config/idomaar-TO-kafka.conf -Didomaar.url=' + self.training_uri + ' -Didomaar.sourceType=file'
        self.executor.run_on_data_stream_manager(flume_command)

        ## TODO CONFIGURE LOG IN ORDER TO TRACK ERRORS AND EXIT FROM ORCHESTRATOR
        ## TODO CONFIGURE FLUME IDOMAAR PLUGIN TO LOG IMPORTANT INFO AND LOG4J TO LOG ONLY ERROR FROM FLUME CLASS

        self._state = OrchestratorState.reading_input

    def prepare(self):
        self.executor.start_datastream()
        self.executor.configure_datastream(self.num_concurrent_recommendation_managers)
        self.start_vm()

    def run(self):
        if self.training_uri is None:
            logger.error("Training dataset is not set!")
            return

        if self.test_uri is None:
            logger.error("Test dataset is not set!")
            return

        logger.warning("WAIT: waiting for machine to be ready")

        while True:
            logger.warning("WAIT: waiting for new message in state ["+ self._state.name +"]"  )
            message = self._socket.recv_multipart()
            logger.info("0MQ: received message: %s " % message)

            if message[0] == 'READY':
                logger.info("INFO: machine started")
                # Tell the computing environment to start reading training data from the kafka queue
                self.send_train()

            elif message[0] == 'OK':
                if self._state == OrchestratorState.reading_input:
                    logger.info("INFO: recommender correctly trained")

                    # TODO DESTINATION FILE MUST BE PASSED FROM COMMAND LINE


                    for reco_manager in self.reco_managers_by_name.itervalues():
                        reco_manager.start()

                    # recommendation_server_0mq = '192.168.22.100:5560'
                    # recommendation_manager_start = "/vagrant/flume-config/startup/recommendation_manager-agent start " + recommendation_server_0mq + " " + str(self.reco_manager_connection_port)
                    # self.executor.run_on_data_stream_manager(recommendation_manager_start)

                    ## TODO CURRENTLY WE ARE TESTING ONLY "FILE" TYPE, WE NEED TO BE ABLE TO CONFIGURE A TEST OF TYPE STREAMING
                    logger.info("Start sending test data to queue")

                    test_data_feed_command = "flume-ng agent --conf /vagrant/flume-config/log4j/test --name a1 --conf-file /vagrant/flume-config/config/idomaar-TO-kafka.conf -Didomaar.url=" + orchestrator.test_uri + " -Didomaar.sourceType=file"
                    self.executor.run_on_data_stream_manager(test_data_feed_command)

                    ## TODO CONFIGURE LOG IN ORDER TO TRACK ERRORS AND EXIT FROM ORCHESTRATOR
                    ## TODO CONFIGURE FLUME IDOMAAR PLUGIN TO LOG IMPORTANT INFO AND LOG4J TO LOG ONLY ERROR FROM FLUME CLASS

                    msg = ['TEST']
                    logger.warn("WAIT: sending message "+ ''.join(msg) +" and wait for response")

                    self._socket.send_multipart(msg)
                    self._state = OrchestratorState.recommending

                elif self._state == OrchestratorState.recommending:
                    logger.info("INFO: recommendations correctly generated, waiting for finished message from recommendation manager agents")

                    reco_manager_message = self.reco_manager_socket.recv_multipart()
                    logger.info("Message from recommendation manager: %s " % reco_manager_message)
                    if reco_manager_message[0] == "FINISHED":
                        reco_manager_name = reco_manager_message[1] if len(reco_manager_message) > 1 else ""
                        reco_manager = self.reco_managers_by_name.get(reco_manager_name)
                        if reco_manager is not None:
                            logger.info("Recommendation manager " + reco_manager_name + "has finished processing recommendation queue, shutting all managers down.")
                            for manager in self.reco_managers_by_name.itervalues(): reco_manager.stop()
                            break
                        else:
                            logger.error("Received FINISHED message from a recommendation manager named " + reco_manager_name + " but no record of this manager is found.")

                    ## TODO RECEIVE SOME STATISTICS FROM THE COMPUTING ENVIRONMENT


            elif message[0] == 'KO':

                if self._state == OrchestratorState.reading_input:
                    logger.error("ERROR: machine failed to start. Process stopped.")
                elif self._state == OrchestratorState.training:
                    logger.error("ERROR: some errors while training the recommender. \
                            Process stopped.")
                elif self._state == OrchestratorState.startRecommending:
                    logger.error("ERROR: some errors while starting the recommender engine.")
                    print message
                elif self._state == OrchestratorState.recommending:
                    logger.error("ERROR: some errors while generating recommendations.\
                            Process stopped.")
                else:
                    logger.error("unknown error")

                break


            else:
                logger.error("Unknown message type " + str(message))
                continue

        logger.info("DO: stop")
        msg = ['STOP']
        self._socket.send_multipart(msg)

        self._socket.close()
        self._context.term()

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
                                       datastream_manager_working_dir=os.path.join(basedir, "datastreammanager"))

    orchestrator = Orchestrator(executor=vagrant_executor)
    orchestrator.training_uri = sys.argv[2]
    orchestrator.test_uri = sys.argv[3]
    orchestrator.computing_env = os.path.join(computing_env_dir, sys.argv[1])
    orchestrator.datastreammanager = os.path.join(basedir, "datastreammanager")

    logger.info("Idomaar base path: %s" % basedir)
    logger.info("Training data URI: %s" % orchestrator.training_uri)
    logger.info("Test data URI: %s" % orchestrator.test_uri)
    logger.info("Computing environment path: %s" % orchestrator.computing_env)

    orchestrator.prepare()
    orchestrator.run()

    # TODO: check if data stream channel is empty (http metrics)
    # TODO: test/evaluate the output

    #logger.info("DO: Stopping computing environment")
    #orchestrator.executor.stop(working_dir=orchestrator.computing_env, subprocess_logger=computing_environment_logger)

    logger.info("Finished.")
