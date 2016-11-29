import logging
from generated_flume_config import FlumeConfig

logger = logging.getLogger("kafka-input-evaluator")

class ReplicatingEvaluatorProxy():
    
    flume_config_base_dir = '/vagrant/flume-config/config'
    
    def __init__(self, executor, idomaar_environment):
        self.executor = executor
        self.environment = idomaar_environment
        
    def feed_file_to_topic(self, data_source, topic_name, conf_file_suffix, kafka_hostport):
        logger.info("{file} is sent to Kafka topic {topic} ".format(file=data_source, topic=topic_name))
        config_file_name = 'idomaar-TO-kafka-direct-' + conf_file_suffix + '.conf'
        config = FlumeConfig(base_dir=self.flume_config_base_dir, template_file_name='idomaar-TO-kafka-direct.conf')
        config.set_value('agent.sinks.kafka_sink.topic', topic_name)
        config.set_value('agent.sinks.kafka_sink.brokerList', kafka_hostport)
        if data_source.url:
            config.set_value('agent.sources.idomaar_source.url', data_source.url)
        if data_source.file_name:
            config.set_value('agent.sources.idomaar_source.fileName', data_source.file_name)
        config.set_value('agent.sources.idomaar_source.format', data_source.format)
        config.set_value('agent.channels.channel.checkpointDir', '/tmp/' + config_file_name + '/flume_data_checkpoint')
        config.set_value('agent.channels.channel.dataDirs', '/tmp/' + config_file_name + '/flume_data')
        config.generate(output_file_name=config_file_name)
        #logger.info("Start feeding data to Flume, Kafka sink topic is {0}".format(topic_name))
        test_data_feed_command = "/opt/apache/flume/bin/flume-ng agent --conf /vagrant/flume-config/log4j/test --name agent --conf-file /vagrant/flume-config/config/generated/" + config_file_name
        self.executor.start_on_data_stream_manager(command=test_data_feed_command, process_name="to-topic-" + conf_file_suffix)
        

    def start_input_feed(self, data_source):
        logger.info("Data is sent to data splitter via Kafka topic " + self.environment.input_topic)
        self.feed_file_to_topic(data_source, self.environment.input_topic, "input", self.environment.kafka_hostport)
        self.feed_file_to_topic(data_source, self.environment.recommendation_requests_topic, "rec-requests", self.environment.kafka_hostport)
        self.feed_file_to_topic(data_source, self.environment.ground_truth_topic, "ground-truth", self.environment.kafka_hostport)
        
    
    def start_splitter(self, data_source):
        logger.info("Would start splitter now.")
        self.start_input_feed(data_source)
