import logging
from generated_flume_config import FlumeConfig

logger = logging.getLogger("kafka-input-evaluator")

class EvaluatorProxy():
    
    def __init__(self, executor, idomaar_environment):
        self.executor = executor
        self.idomaar_environment = idomaar_environment
        
        
    def start_input_feed(self):
        logger.info("Data is sent to data splitter via Kafka topic " + self.config.input_topic)
        config = FlumeConfig(base_dir=self.flume_config_base_dir, template_file_name='idomaar-TO-kafka-direct.conf')
        config.set_value('agent.sinks.kafka_sink.topic', self.config.input_topic)
        config.set_value('agent.sources.idomaar_source.fileName', self.config.data_source)
        config.generate()
        logger.info("Start feeding data to Flume, Kafka sink topic is {0}".format(self.config.input_topic))
        test_data_feed_command = "/opt/apache/flume/bin/flume-ng agent --conf /vagrant/flume-config/log4j/test --name agent --conf-file /vagrant/flume-config/config/generated/idomaar-TO-kafka-direct.conf"
        self.executor.start_on_data_stream_manager(command=test_data_feed_command, process_name="to-kafka-flume")
    
    def start_splitter(self):
        
        env_variables = {'TERM': 'linux', 'ZOOKEEPER_CONNECTION': self.idomaar_environment.zookeeper_hostport,
                         'KAFKA_CONNECTION': self.idomaar_environment.kafka_hostport, 
                         'INPUT_TOPIC': self.idomaar_environment.input_topic,
                          'RECOMMENDATION_REQUESTS_TOPIC': self.idomaar_environment.recommendation_requests_topic,
                          'GROUND_TRUTH_TOPIC': self.idomaar_environment.ground_truth_topic,
                          'SPARK_CLASSPATH': '`cat /usr/share/ivy/path.txt`'}
        spark_shell_command = '/opt/apache/spark/bin/spark-shell -i splitterdemo.script'
        
        compound_command = "ssh vagrant@{evaluator_host} cd {evaluator_script_folder}; {env_variables} {spark_shell_command}".format(
                            evaluator_host=self.idomaar_environment.evaluator_ip,
                            evaluator_script_folder='/vagrant/evaluation/scala',
                            env_variables=' '.join([key + "=" + value for key,value in env_variables.iteritems()]),
                            spark_shell_command = spark_shell_command)
        
        self.executor.start_on_data_stream_manager(command=compound_command, process_name="splitting", exit_on_failure=False)
        
