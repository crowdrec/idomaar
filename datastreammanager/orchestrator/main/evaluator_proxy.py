

class EvaluatorProxy():
    
    def __init__(self, executor, idomaar_environment):
        self.executor = executor
        self.idomaar_environment = idomaar_environment
    
    def start_splitter(self):
        
        env_variables = {'TERM': 'linux', 'ZOOKEEPER_CONNECTION': self.idomaar_environment.zookeeper_hostport,
                         'KAFKA_CONNECTION': self.idomaar_environment.kafka_hostport, 
                         'INPUT_TOPIC': self.idomaar_environment.input_topic,
                          'RECOMMENDATION_REQUESTS_TOPIC': self.idomaar_environment.recommendation_requests_topic,
                          'GROUND_TRUTH_TOPIC': self.idomaar_environment.ground_truth_topic,
                          'SPARK_CLASSPATH': '`cat /usr/share/ivy/path.txt`'}
        spark_shell_command = '/usr/bin/spark-shell -i splitterdemo.script'
        
        compound_command = "ssh vagrant@{evaluator_host} cd {evaluator_script_folder}; {env_variables} {spark_shell_command}".format(
                            evaluator_host=self.idomaar_environment.evaluator_ip,
                            evaluator_script_folder='/vagrant/evaluation/scala',
                            env_variables=' '.join([key + "=" + value for key,value in env_variables.iteritems()]),
                            spark_shell_command = spark_shell_command)
        
        self.executor.start_on_data_stream_manager(command=compound_command, process_name="splitting", exit_on_failure=False)
        
