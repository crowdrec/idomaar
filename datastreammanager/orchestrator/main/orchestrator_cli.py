import json
import logging
import os
import colorlog
from plumbum import cli
import sys
from local_executor import LocalExecutor
from orchestrator import Orchestrator
from vagrant_executor import VagrantExecutor

logger = logging.getLogger("orchestrator")

class OrchestratorCli(cli.Application):

    PROGNAME = "orchestrator"
    VERSION = "0.0.1"

    host_orchestrator = cli.Flag(["--host-orchestrator"], help = "If given, the orchestrator assumes to be running on the host OS, and execute all datastream commands via vagrant."+
        " The default assumption is that the orchestrator is running on the same (virtual) box as the datastream components (hence doesn't have to go via vagrant)." )

    new_topic = cli.Flag(["--new-topic"], help = "If given, new Kafka topics will be created for data and recommendations feeds.", excludes = ['--data-topic', '--recommendations-topic'] )

    comp_env = None
    recommendation_target = 'fs:/tmp/recommendations'
    data_topic = 'data'
    recommendations_topic = 'recommendations'
    config_file = 'default-config.json'

    #Configuration parameters from JSON config file

    #Number of threads requesting recommendations
    recommendation_request_thread_count = 1
    #Messages per sec sent to the computing environment. 0 means no limit
    messages_per_sec = 0

    @cli.switch("--comp-env-dir", str)
    def get_comp_env(self, directory):
        """The relative path to the computing environment vagrant directory. This only makes sense if the orchestrator runs on the same host as the computing environment."""
        self.comp_env = directory

    @cli.switch("--comp-env-address", str, mandatory=True, list=True)
    def get_computing_environment_address(self, address):
        """The URL of the computing environment, either tcp://hostname:port for ZMQ communication or http://hostname:port for HTTP communication.
        If multiple addresses are given, only the last one is taken into account. This facilitates parameter overriding when called from shell scritps (that is,
        parameter lists to be merged can simply be concatenated)."""
        address_used = address[-1]
        logger.info("{0} computing environment addresses given, using the last one {1}".format(len(address), address_used))
        self.computing_environment_address = address_used

    @cli.switch("--config-file", str)
    def get_config_file(self, config_file):
        """Orchestrator configuration file, defaults to default-config.json"""
        self.config_file = config_file

    @cli.switch("--training-uri", str, mandatory=True)
    def get_training_uri(self, training_uri):
        """The location of the training data."""
        self.training_uri = training_uri

    @cli.switch("--test-uri", str, mandatory=True)
    def get_test_uri(self, test_uri):
        """The location of the test data."""
        self.test_uri = test_uri

    @cli.switch("--recommendation-target", str)
    def get_recommendation_target(self, target):
        """The location where recommendations are placed."""
        if not (target.startswith('fs:') or target.startswith('hdfs:')): raise "Recommendation target must start with fs: or hdfs: to specify target type."
        self.recommendation_target = target

    @cli.switch("--data-topic", str)
    def get_data_topic(self, topic):
        """The Kafka topic where train and test data is fed."""
        self.data_topic = topic

    @cli.switch("--recommendations-topic", str)
    def get_recommendation_topic(self, topic):
        """The Kafka topic where recommendations are fed."""
        self.recommendations_topic = topic


    def main(self):
        # TODO RECOMMENDATION HOSTNAME MUST BE EXTRACTED FROM MESSAGES
        logger.info("Training data URI: %s" % self.training_uri)
        logger.info("Test data URI: %s" % self.test_uri)
        logger.info("Computing environment path: %s" % self.comp_env)
        basedir = os.path.abspath("../../")
        logger.info("Idomaar base path: %s" % basedir)

        config_file_location = os.path.join('/vagrant', self.config_file)
        with open(config_file_location) as input_file:
            config_json=input_file.read()
        config_data = json.loads(config_json)
        logger.info("Configuration loaded from file {0} : {1}".format(config_file_location, config_data))
        if 'recommendation_request_thread_count' in config_data: self.recommendation_request_thread_count = config_data['recommendation_request_thread_count']
        if 'messages_per_sec' in config_data: self.messages_per_sec = config_data['messages_per_sec']

        if self.host_orchestrator:
            datastreammanager = os.path.join(basedir, "datastreammanager")
            computing_env_dir = os.path.join(basedir, "computingenvironments")
            executor = VagrantExecutor(reco_engine_hostport='192.168.22.100:5560', orchestrator_port=2761,
                                           datastream_manager_working_dir=datastreammanager, recommendation_timeout_millis=4000, computing_env_dir=computing_env_dir)
        else:
            logger.info("Using local executor.")
            datastreammanager = "/vagrant"
            executor = LocalExecutor(reco_engine_hostport='192.168.22.100:5560', orchestrator_port=2761,
                                               datastream_manager_working_dir=datastreammanager, recommendation_timeout_millis=4000)

        orchestrator = Orchestrator(executor=executor, datastreammanager=datastreammanager, config=self)

        try:
            orchestrator.run()
        except Exception:
            logger.exception("Exception occurred, hard shutdown.")
            os._exit(-1)

        logger.info("Finished.")

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
    OrchestratorCli.run()