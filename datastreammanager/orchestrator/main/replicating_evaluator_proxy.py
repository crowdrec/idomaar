import logging
from generated_flume_config import FlumeConfig

logger = logging.getLogger("kafka-input-evaluator")

class ReplicatingEvaluatorProxy():
    
    flume_config_base_dir = '/vagrant/flume-config/config'
    
    def __init__(self, executor, idomaar_environment):
        self.executor = executor
        self.environment = idomaar_environment
        
    def feed_file_to_topic(self, input_file_name, topic_name, conf_file_suffix, file_format):
        logger.info("{file} is sent to Kafka topic {topic} ".format(file=input_file_name, topic=topic_name))
        config_file_name = 'idomaar-TO-kafka-direct-' + conf_file_suffix + '.conf'
        config = FlumeConfig(base_dir=self.flume_config_base_dir, template_file_name='idomaar-TO-kafka-direct.conf')
        config.set_value('agent.sinks.kafka_sink.topic', topic_name)
        config.set_value('agent.sources.idomaar_source.fileName', input_file_name)
        config.set_value('agent.sources.idomaar_source.format', file_format)
        config.set_value('agent.channels.channel.checkpointDir', '/tmp/' + config_file_name + '/flume_data_checkpoint')
        config.set_value('agent.channels.channel.dataDirs', '/tmp/' + config_file_name + '/flume_data')
        
        config.generate(output_file_name=config_file_name)
        #logger.info("Start feeding data to Flume, Kafka sink topic is {0}".format(topic_name))
        test_data_feed_command = "/opt/apache/flume/bin/flume-ng agent --conf /vagrant/flume-config/log4j/test --name agent --conf-file /vagrant/flume-config/config/generated/" + config_file_name
        self.executor.start_on_data_stream_manager(command=test_data_feed_command, process_name="to-topic-" + conf_file_suffix)
        
    def guess_file_format(self, file_name):
        if file_name.endswith('.gz') or file_name.endswith('.gzip'): return 'gzip'
        else: return 'plain'
        
        
    def start_input_feed(self, input_file_name):
        logger.info("Data is sent to data splitter via Kafka topic " + self.environment.input_topic)
        file_format = self.guess_file_format(input_file_name)
        logger.info("Guessed file format is " + file_format)
        self.feed_file_to_topic(input_file_name, self.environment.input_topic, "input", file_format)
        self.feed_file_to_topic(input_file_name, self.environment.recommendation_requests_topic, "rec-requests", file_format)
        self.feed_file_to_topic(input_file_name, self.environment.ground_truth_topic, "ground-truth", file_format)
        
    
    def start_splitter(self, input_file_name):
        logger.info("Would start splitter now.")
        self.start_input_feed(input_file_name)
        
