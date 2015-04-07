import  zmq
import datetime
import  os
import logging
import yaml
import time
from generated_flume_config import FlumeConfig
from http_comp_env import HttpComputingEnvironmentProxy
from recommendation_manager import RecommendationManager
from util import timed_exec
from zmq_comp_env import ZmqComputingEnvironmentProxy

logger = logging.getLogger("orchestrator")

class Orchestrator(object):

    flume_config_base_dir = '/vagrant/flume-config/config'

    def __init__(self, executor, datastreammanager, config):
        self.config = config
        self.recommendation_target = config.recommendation_target
        self.executor = executor
        self.datastreammanager = datastreammanager

        self.training_uri = config.training_uri
        self.test_uri = config.test_uri

        if config.computing_environment_address.startswith("tcp://"): self.comp_env_proxy = ZmqComputingEnvironmentProxy(config.computing_environment_address)
        elif config.computing_environment_address.startswith("http://"): self.comp_env_proxy = HttpComputingEnvironmentProxy(config.computing_environment_address)
        else: raise "Unrecognized computing environment address."

        self.reco_manager_socket = zmq.Context().socket(zmq.REP)
        self.reco_manager_socket.bind('tcp://*:%s' % self.executor.orchestrator_port)

        self.reco_managers_by_name = self.create_recommendation_managers(self.config.recommendation_request_thread_count)

    def create_recommendation_managers(self, count):
        return {"RM" + str(i): RecommendationManager("RM" + str(i), self.executor, self.flume_config_base_dir) for i in range(count)}

    def read_yaml_config(self, file_name):
        with open(file_name, 'r') as input_file:
            return yaml.load(input_file)

    def send_train(self, zookeeper_hostport):
        """ Tell the computing environment to start reading training data from the kafka queue
            Instructs the flume agent on the datastreammanager vm to start streaming training data. Then sends a TRAIN message to the computing environment, and
            wait until training is complete."""
        logger.info("Sending TRAIN message to computing environment and waiting for training to be ready ...")
        train_response, took_mins = timed_exec(lambda: self.comp_env_proxy.send_train(zookeeper_hostport=zookeeper_hostport, kafka_topic=self.config.data_topic))
        if train_response[0] == 'OK':
            logger.info("Training completed successfully, took {0} minutes.".format(took_mins))
            recommendation_endpoint = train_response[1]
            return recommendation_endpoint
        if train_response[0] == 'KO':
            raise Exception("Computing environment answered with 'KO': error occurred during recommendation model training.")
        else:
            raise Exception("Unexpected message received from computing environment." + str(train_response))

    def read_zookeeper_hostport(self):
        datastream_config = self.read_yaml_config(os.path.join(self.datastreammanager, "vagrant.yml"))
        datastream_ip_address = datastream_config['box']['ip_address']
        zookeeper_port = datastream_config['zookeeper']['port']
        zookeeper_hostport = "{host}:{port}".format(host=datastream_ip_address, port=zookeeper_port)
        return zookeeper_hostport

    def create_topic_names(self):
        if self.config.new_topic:
            now = datetime.datetime.now()
            suffix = "{mo}{d}-{h}{mi}{sec}".format(y=now.year,mo=now.month,d=now.day,h=now.hour,mi=now.minute,sec=now.second)
            self.config.data_topic = "data-" + suffix
            self.config.recommendations_topic = "recommendations-" + suffix
        logger.info("Using Kafka topic names: {0} for data, {1} for recommendations".format(self.config.data_topic, self.config.recommendations_topic))

    def feed_training_data(self):
        self.create_flume_config('idomaar-TO-kafka-train.conf')
        logger.info("Start feeding training data, data reader for training data uri=[" + str(self.training_uri) + "]")
        flume_command = 'flume-ng agent --conf /vagrant/flume-config/log4j/training --name a1 --conf-file /vagrant/flume-config/config/generated/idomaar-TO-kafka-train.conf -Didomaar.url=' + self.training_uri + ' -Didomaar.sourceType=file'
        self.executor.run_on_data_stream_manager(flume_command)

    def feed_test_data(self):
        if self.config.data_to_recommendations: 
            logger.info("Data treated as recommendation requests, sending directly ")
            config = FlumeConfig(base_dir=self.flume_config_base_dir, template_file_name='idomaar-TO-kafka-direct.conf')
            config.set_value('agent.sinks.kafka_sink.topic', self.config.recommendations_topic)
            config.generate()
            logger.info("Start feeding data to Flume, Kafka sink topic is {0}".format(selc.config.recommendations_topic))
            test_data_feed_command = "flume-ng agent --conf /vagrant/flume-config/log4j/test --name a1 --conf-file /vagrant/flume-config/config/generated/idomaar-TO-kafka-direct.conf"
            self.executor.run_on_data_stream_manager(test_data_feed_command)
        else:
            self.create_flume_config('idomaar-TO-kafka-test.conf')
            logger.info("Start feeding test data to queue")
            ## TODO CURRENTLY WE ARE TESTING ONLY "FILE" TYPE, WE NEED TO BE ABLE TO CONFIGURE A TEST OF TYPE STREAMING
            test_data_feed_command = "flume-ng agent --conf /vagrant/flume-config/log4j/test --name a1 --conf-file /vagrant/flume-config/config/generated/idomaar-TO-kafka-test.conf -Didomaar.url=" + self.test_uri + " -Didomaar.sourceType=file"
            self.executor.run_on_data_stream_manager(test_data_feed_command)

    def create_flume_config(self, template_file_name):
        config = FlumeConfig(base_dir=self.flume_config_base_dir, template_file_name=template_file_name)
        config.set_value('a1.sinks.kafka_data.topic', self.config.data_topic)
        config.set_value('a1.sinks.kafka_rec.topic', self.config.recommendations_topic)
        config.generate()

    def run(self):
        self.create_topic_names()

        datastream_config = self.read_yaml_config(os.path.join(self.datastreammanager, "vagrant.yml"))
        datastream_ip_address = datastream_config['box']['ip_address']
        #TODO: properly handle orchestrator location
        orchestrator_ip = datastream_ip_address
        zookeeper_port = datastream_config['zookeeper']['port']
        zookeeper_hostport = "{host}:{port}".format(host=datastream_ip_address, port=zookeeper_port)

        self.executor.start_datastream()
        self.executor.configure_datastream(self.config.recommendation_request_thread_count, zookeeper_hostport, config=self.config)
        self.executor.start_computing_environment()
        self.comp_env_proxy.connect(timeout_secs=20)

        if not self.config.skip_training_cycle:
            self.feed_training_data()
            recommendation_endpoint = self.send_train(zookeeper_hostport=zookeeper_hostport)
            logger.info("Received recommendation endpoint " + str(recommendation_endpoint))
        else:
            logger.info("Training phase skipped, using {0} as recommendation endpoint.".format(self.config.computing_environment_address)) 
            recommendation_endpoint = self.config.computing_environment_address

        self.feed_test_data()
        manager = self.reco_managers_by_name.itervalues().next()
        manager.create_configuration(self.recommendation_target, communication_protocol=self.comp_env_proxy.communication_protocol, recommendations_topic=self.config.recommendations_topic)
        for reco_manager in self.reco_managers_by_name.itervalues():
            reco_manager.start(orchestrator_ip, recommendation_endpoint)

        ## TODO CONFIGURE LOG IN ORDER TO TRACK ERRORS AND EXIT FROM ORCHESTRATOR
        ## TODO CONFIGURE FLUME IDOMAAR PLUGIN TO LOG IMPORTANT INFO AND LOG4J TO LOG ONLY ERROR FROM FLUME CLASS

        self.comp_env_proxy.send_test()
        logger.info("INFO: recommendations correctly generated, waiting for finished message from recommendation manager agents")

        reco_manager_message = self.reco_manager_socket.recv_multipart()
        logger.info("Message from recommendation manager: %s " % reco_manager_message)
        self.reco_manager_socket.send("OK")
        if reco_manager_message[0] == "FINISHED":
            reco_manager_name = reco_manager_message[1] if len(reco_manager_message) > 1 else ""
            reco_manager = self.reco_managers_by_name.get(reco_manager_name)
            if reco_manager is not None:
                logger.info("Recommendation manager " + reco_manager_name + "has finished processing recommendation queue.")
                logger.warn("Waiting 20 secs to work around Flume issue FLUME-1318.")
                time.sleep(20)
                logger.info("Shutting all managers down ...")
                for manager in self.reco_managers_by_name.itervalues(): manager.stop()
            else:
                logger.error("Received FINISHED message from a recommendation manager named " + reco_manager_name + " but no record of this manager is found.")

        ## TODO RECEIVE SOME STATISTICS FROM THE COMPUTING ENVIRONMENT

        # TODO: check if data stream channel is empty (http metrics)
        # TODO: test/evaluate the output

        self.comp_env_proxy.send_stop()
        self.close()

    def close(self):
        logger.info("Orchestrator closing...")
        self.comp_env_proxy.close()
        logger.info("Orchestrator shutdown.")