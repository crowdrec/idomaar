import  zmq
import  os
from    enum import Enum
import  subprocess
import sys
import logging
import colorlog

logger = logging.getLogger("orchestrator")
datastream_logger = logging.getLogger("datastream")
computing_environment_logger = logging.getLogger("computing_environment")

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

        self.reco_manager_connection_port = 2761
        self.reco_manager_socket = zmq.Context().socket(zmq.REP)
        self.reco_manager_socket.bind('tcp://*:%s' % self.reco_manager_connection_port)

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
        logger.info("DO: starting data stream")
        return self.execute_vagrant_command(command=['vagrant', 'up'], working_dir=self.datastreammanager, subprocess_logger=datastream_logger)

    def start_vm(self):
        if self.computing_env is None:
            logger.error("computing env not set!")
            return
        logger.info("DO: starting Computing environment")
        return self.execute_vagrant_command(command=['vagrant', 'up'], working_dir=self.computing_env, subprocess_logger=computing_environment_logger)

    def stop_vm(self):
        logger.info("DO: Stopping computing environment")
        return self.execute_vagrant_command(command=['vagrant', 'halt'], working_dir=self.computing_env, subprocess_logger=computing_environment_logger)

    def execute_vagrant_command(self, command, working_dir, subprocess_logger, exit_on_failure=True):
        vagrant_command_string = ' '.join(command)
        process = subprocess.Popen(command, env=os.environ, cwd=working_dir, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=False)
        while True:
            line = process.stdout.readline()
            if line: subprocess_logger.info(line.strip())
            else: break
        exit_code = process.wait()
        if not exit_on_failure: return exit_code
        if exit_code != 0:
            logger.error("Error occurred while executing {name} in directory {working_dir}, exit code is {code}. Exiting.".format(name=vagrant_command_string, working_dir=working_dir, code=exit_code))
            sys.exit(1)
        else: logger.info("Command '" + vagrant_command_string + "' is successful.")
        return exit_code


    def run_on_data_stream_manager(self, command, exit_on_failure = True):
        """
        Run a command on the data stream manager VM. Returns the subprocess exit code.
        """
        vagrant_command = ["vagrant", "ssh", "-c", "sudo " + command]
        vagrant_command_string = ' '.join(vagrant_command)
        logger.info("On data stream manager, executing command " + vagrant_command_string)
        self.execute_vagrant_command(command=vagrant_command, working_dir=self.datastreammanager, subprocess_logger=datastream_logger, exit_on_failure=exit_on_failure)

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
        self.run_on_data_stream_manager(flume_command)

        ## TODO CONFIGURE LOG IN ORDER TO TRACK ERRORS AND EXIT FROM ORCHESTRATOR
        ## TODO CONFIGURE FLUME IDOMAAR PLUGIN TO LOG IMPORTANT INFO AND LOG4J TO LOG ONLY ERROR FROM FLUME CLASS

        self._state = OrchestratorState.reading_input


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
                    # TODO RECOMMENDATION HOSTNAME MUST BE EXTRACTED FROM MESSAGES
                    recommendation_server_0mq = '192.168.22.100:5560'

                    recommendation_manager_start = "/vagrant/flume-config/startup/recommendation_manager-agent start " + recommendation_server_0mq + " " + str(self.reco_manager_connection_port)
                    self.run_on_data_stream_manager(recommendation_manager_start)

                    ## TODO CURRENTLY WE ARE TESTING ONLY "FILE" TYPE, WE NEED TO BE ABLE TO CONFIGURE A TEST OF TYPE STREAMING
                    logger.info("Start sending test data to queue")

                    test_data_feed_command = "flume-ng agent --conf /vagrant/flume-config/log4j/test --name a1 --conf-file /vagrant/flume-config/config/idomaar-TO-kafka.conf -Didomaar.url=" + orchestrator.test_uri + " -Didomaar.sourceType=file"
                    self.run_on_data_stream_manager(test_data_feed_command)

                    ## TODO CONFIGURE LOG IN ORDER TO TRACK ERRORS AND EXIT FROM ORCHESTRATOR
                    ## TODO CONFIGURE FLUME IDOMAAR PLUGIN TO LOG IMPORTANT INFO AND LOG4J TO LOG ONLY ERROR FROM FLUME CLASS

                    msg = ['TEST']
                    logger.warn("WAIT: sending message "+ ''.join(msg) +" and wait for response")

                    self._socket.send_multipart(msg)
                    self._state = OrchestratorState.recommending

                elif self._state == OrchestratorState.recommending:
                    logger.info("INFO: recommendations correctly generated")

                    # TODO TRACK IF KAFKA RECOMMENDATION QUEUE IS EMPTY, OTHERWISE WAIT FOR DEQUEUE
                    reco_manager_message = self.reco_manager_socket.recv_multipart()
                    logger.info("Message from recommendation manager: %s " % reco_manager_message)
                    if reco_manager_message[0] == "FINISHED":
                        logger.info("Recommendation manager has finished processing recommendation queue, shutting it down and then exiting.")
                        recommendation_manager_stop = "/vagrant/flume-config/startup/recommendation_manager-agent stop"
                        self.run_on_data_stream_manager(recommendation_manager_stop)
                        break

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
                print ("unknown message type", message)
                continue

        logger.info("DO: stop")
        msg = ['STOP']
        self._socket.send_multipart(msg)

        logger.warning("INFO: stopping recommendation manager on data stream manager")

        recommendation_manager_stop = "/vagrant/flume-config/startup/recommendation_manager-agent stop"
        self.run_on_data_stream_manager(recommendation_manager_stop)

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

    orchestrator = Orchestrator()
    orchestrator.training_uri = sys.argv[2]
    orchestrator.test_uri = sys.argv[3]
    orchestrator.computing_env = os.path.join(computing_env_dir, sys.argv[1])
    orchestrator.datastreammanager = os.path.join(basedir, "datastreammanager")

    logger.info("Idomaar base path: %s" % basedir)
    logger.info("Training data URI: %s" % orchestrator.training_uri)
    logger.info("Test data URI: %s" % orchestrator.test_uri)
    logger.info("Computing environment path: %s" % orchestrator.computing_env)

    orchestrator.start_datastream()

    # TODO: create/check data for validation

    orchestrator.start_vm()

    orchestrator.run()

    # TODO: check if data stream channel is empty (http metrics)
    # TODO: test/evaluate the output

    # orchestrator.stop_vm()

    logger.info("Finished.")
