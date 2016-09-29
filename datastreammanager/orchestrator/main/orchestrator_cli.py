import json
import logging
import os
import colorlog
from plumbum import cli
import sys
from local_executor import LocalExecutor
from orchestrator import Orchestrator
from vagrant_executor import VagrantExecutor
from urlparse import urlparse

logger = logging.getLogger("orchestrator")

class OrchestratorCli(cli.Application):

    PROGNAME = "orchestrator"
    VERSION = "0.0.1"

    host_orchestrator = cli.Flag(["--host-orchestrator"], help = "If given, the orchestrator assumes to be running on the host OS, and execute all datastream commands via vagrant."+
        " The default assumption is that the orchestrator is running on the same (virtual) box as the datastream components (hence doesn't have to go via vagrant)." )

    new_topic = cli.Flag(["--new-topic"], help = "If given, new Kafka topics will be created for data and recommendations feeds.", excludes = ['--data-topic', '--recommendations-topic'] )
    
    skip_training_cycle = cli.Flag(["--skip-training"], help = "If given, the training phase in the orchestrator lifecycle is skipped.")
    
    no_control_messages = cli.Flag(["--no-control-messages", '-n'], help = "If given, the orchestrator won't send control messages to the computing environment.")
    
    comp_env = None
    data_source = None
    recommendation_target = 'fs:/tmp/recommendations'
    
    #The data_topic is meaningless and should be removed
    data_topic = 'data'
    input_topic = 'input'
    recommendation_requests_topic = 'recommendation-requests'
    recommendation_results_topic = 'recommendation-results'
    ground_truth_topic = 'ground-truth'
    
    input_data = 'split'
    newsreel = False
    
    
    config_file = 'default-config.json'
    num_threads = 1

    #Configuration parameters from JSON config file

    #Number of threads requesting recommendations
    recommendation_request_thread_count = 1
    #Messages per sec sent to the computing environment. 0 means no limit
    messages_per_sec = 0
    
    
    log_level = 'info'

    @cli.switch("--comp-env-dir", str)
    def get_comp_env(self, directory):
        """The relative path to the computing environment vagrant directory. This only makes sense if the orchestrator runs on the same host as the computing environment."""
        self.comp_env = directory

    @cli.switch(["--comp-env-address", "--address", "-a"], str, mandatory=True, list=True)
    def get_computing_environment_address(self, address):
        """The URL of the computing environment, either tcp://hostname:port for ZMQ communication or http://hostname:port for HTTP communication.
        If multiple addresses are given, only the last one is taken into account. This facilitates parameter overriding when called from shell scritps (that is,
        parameter lists to be merged can simply be concatenated)."""
        address_used = address[-1]
        logger.info("{0} computing environment addresses given, using the last one {1}".format(len(address), address_used))
        self.computing_environment_address = address_used
        try:
            self.computing_environment_url = urlparse(address_used)
        except:
            logger.error("Cannot parse computing environment address URL.")
            raise
        

    @cli.switch("--config-file", str)
    def get_config_file(self, config_file):
        """Orchestrator configuration file, defaults to default-config.json"""
        self.config_file = config_file

    @cli.switch("--training-uri", str)
    def get_training_uri(self, training_uri):
        """The location of the training data."""
        self.training_uri = training_uri
        self.input_data = 'test'

    @cli.switch("--test-uri", str)
    def get_test_uri(self, test_uri):
        """The location of the test data."""
        self.test_uri = test_uri
        self.input_data = 'test'
        
    @cli.switch("--data-source", str, excludes=['--training-uri', '--test-uri'])
    def get_data_source(self, data_source):
        """Location of the data. This option can be used in cases (e.g. for Newsreel) when there is one single source of data. Cannot be used
        together with the --training-uri, --test-uri switches."""
        self.data_source = data_source
        
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
        
    @cli.switch("--input-data", str)
    def get_input_data(self, input_data, requires = ["--data-source"]):
        """Specifies how to treat input data from the source:
            test: feed to the Kafka test topic
            split: feed to the splitter
            recommend: feed to the Kafka recommendation requests topic
         Requires the --data-source switch."""
        if input_data not in ['test', 'split', 'recommend']: raise 'Input data must be either "test", "split" or "recommend".'
        self.input_data = input_data 
        
    @cli.switch("--newsreel")
    def get_newsreel(self, requires=['--data-source']):
        """Use the settings relevant for the Newsreel competition Task 2. Equivalent to the switches --skip-training --input-data split --no-control-messages. 
        It will check that the computing environment communication protocol is HTTP or HTTPS."""
        self.newsreel = True
        self.skip_training_cycle = True
        self.input_data = "split"
        self.no_control_messages = True
        if not self.computing_environment_url.scheme in ['http', 'https']: raise Exception("For Newsreel, the computing environment URL must have scheme http or https.")
        
    @cli.switch("--num-threads", int)
    def get_num_threads(self, num_threads):
        """Use the specified number of threads (processes) for requesting recommendations."""
        self.num_threads = num_threads 
        
    @cli.switch("--log-level", str)
    def get_log_level(self, log_level):
        """Log level"""
        self.log_level = log_level
        
    def setup_logging(self):
        root_logger = logging.getLogger()
        root_logger.setLevel(self.log_level.upper())
        root_logger.info("Log level has been set to " + self.log_level)
 
    def main(self):
        self.setup_logging()
        if self.data_source is not None:
            logger.info("Data source: {0}".format(self.data_source))
        else:
            if self.training_uri is not None: logger.info("Training data URI: %s" % self.training_uri)
            elif not self.skip_training_cycle: raise "No training URI is set (and training is required)."
            if self.test_uri is not None: logger.info("Test data URI: %s" % self.test_uri)
            else: raise "No test URI is set."
            
        logger.debug("Computing environment path: %s" % self.comp_env)
        basedir = os.path.abspath("../../")
        logger.debug("Idomaar base path: %s" % basedir)

        config_file_location = os.path.join('/vagrant', self.config_file)
        with open(config_file_location) as input_file:
            config_json=input_file.read()
        config_data = json.loads(config_json)
        logger.debug("Configuration loaded from file {0} : {1}".format(config_file_location, config_data))
        if 'recommendation_request_thread_count' in config_data: self.recommendation_request_thread_count = config_data['recommendation_request_thread_count']
        if 'messages_per_sec' in config_data: self.messages_per_sec = config_data['messages_per_sec']

        if self.host_orchestrator:
            datastreammanager = os.path.join(basedir, "datastreammanager")
            computing_env_dir = os.path.join(basedir, "computingenvironments")
            executor = VagrantExecutor(reco_engine_hostport='192.168.22.100:5560', orchestrator_port=2761,
                                           datastream_manager_working_dir=datastreammanager, recommendation_timeout_millis=4000, computing_env_dir=computing_env_dir)
        else:
            logger.debug("Using local executor.")
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

def initial_logging(logger_to_conf):
    logger_to_conf.setLevel("INFO")
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
    initial_logging(logging.getLogger())
    OrchestratorCli.run()
