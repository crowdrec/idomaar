import logging
import os
import subprocess
import sys
from threading import Thread
from orchestrator_log_forward import relog

logger = logging.getLogger("orchestrator:execute")
datastream_logger = logging.getLogger("datastream")

class LocalExecutor:
    """
    Run vagrant commands to actually execute operations initiated by the orchestrator.
    """

    def __init__(self, reco_engine_hostport, orchestrator_port, datastream_manager_working_dir, recommendation_timeout_millis):
        """
        :param reco_engine_hostport: host and port of the recommendation engine
        :param orchestrator_port: used by the recommendation manager agents
        """
        self.recommendation_timeout_millis = recommendation_timeout_millis
        self.orchestrator_port = orchestrator_port
        self.reco_engine_hostport = reco_engine_hostport
        self.datastream_manager_working_dir = datastream_manager_working_dir

    def run_on_data_stream_manager(self, command, exit_on_failure=True, capture_output=False, default_relog_level='info'):
        """
        Run a command on the data stream manager VM. Returns the subprocess exit code.
        """
        command_list = command.split(" ")
        command_list.insert(0, "sudo")
        vagrant_command_string = ' '.join(command_list)
        logger.debug("On data stream manager, executing command " + vagrant_command_string)
        result = self.process_runner(command=command_list, working_dir=self.datastream_manager_working_dir,
                                     subprocess_logger=datastream_logger, exit_on_failure=exit_on_failure, default_relog_level=default_relog_level)
        if capture_output: return result
        else: return result[0]
        
    def start_on_data_stream_manager(self, command, process_name, exit_on_failure=True):
        """Start a command asynchronously on the data stream manager VM."""
        command_list = command.split(" ")
        command_list.insert(0, "sudo")
        result = self.execute_in_background(command=command_list, working_dir=self.datastream_manager_working_dir,
                                     subprocess_logger=logging.getLogger("bg:" + process_name), exit_on_failure=exit_on_failure)
    
    def process_runner(self, command, working_dir, subprocess_logger, exit_on_failure=False, default_relog_level='info'):
        command_string = ' '.join(command)
        subprocess_logger.debug("Starting process " + command_string)
        output_lines = list()
        process = subprocess.Popen(command, env=os.environ, cwd=working_dir, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=False)
        while True:
            line = process.stdout.readline()
            if line: 
                relog(subprocess_logger, line.strip(), default=default_relog_level)
                output_lines.append(line)
            else: break
        exit_code = process.wait()
        if not exit_on_failure:
            subprocess_logger.info("Process exited with exit code {0}".format(exit_code))
            output_lines.insert(0,exit_code)
            return output_lines
        elif exit_code == 130:
            logger.warn("Exit code 130 received: process {name} is interrupted.".format(name=command_string))
        elif exit_code != 0:
            logger.error("Error occurred while executing {name} in directory {working_dir}, exit code is {code}. Exiting.".format(name=command_string, working_dir=working_dir, code=exit_code))
            sys.exit(1)
        else: logger.debug("Command '" + command_string + "' is successful.")
        return output_lines
    
    def execute_in_background(self, command, working_dir, subprocess_logger, exit_on_failure):
        vagrant_command_string = ' '.join(command)
        logger.debug("Executing command in background " + vagrant_command_string)
        Thread(target=lambda: self.process_runner(command, working_dir, subprocess_logger, exit_on_failure)).start()

    def start_recommendation_manager(self, name, orchestrator_ip, recommendation_endpoint):
        """:param name: The name of the recommendation manager agent"""
        logger.info("Starting recommendation manager " + name)
        orchestrator_connection = "tcp://{ip_address}:{port}".format(ip_address=orchestrator_ip, port=self.orchestrator_port)
        recommendation_manager_start = ' '.join(["/vagrant/flume-config/startup/recommendation_manager-agent start", name, recommendation_endpoint, orchestrator_connection, str(self.recommendation_timeout_millis)])
        self.run_on_data_stream_manager(recommendation_manager_start)
        
    def start_simple_recommendation_manager(self, name, orchestrator_ip, recommendation_endpoint):
        logger.info("Starting recommendation manager")
        orchestrator_connection = "tcp://{ip_address}:{port}".format(ip_address=orchestrator_ip, port=self.orchestrator_port)
        start_manager_command = ("flume-ng agent --conf /vagrant/flume-config/log4j/recommendation-manager --name a1 --conf-file /vagrant/flume-config/config/generated/kafka_recommendations_generated.conf " 
        + "-Didomaar.recommendation.hostname={recommendation_endpoint} -Didomaar.orchestrator.hostname={orchestrator_connection} " +
        " -Didomaar.recommendation.manager.name=rm0 -Didomaar.recommendation.timeout.millis=2000").format(recommendation_endpoint=recommendation_endpoint, orchestrator_connection=orchestrator_connection)
        self.start_on_data_stream_manager(command=start_manager_command, process_name="reco-manager")

    def stop_recommendation_manager(self, name):
        logger.info("Stopping recommendation manager " + name)
        recommendation_manager_stop = "/vagrant/flume-config/startup/recommendation_manager-agent stop " + name
        self.run_on_data_stream_manager(recommendation_manager_stop)

    def execute(self, command, working_dir, subprocess_logger, exit_on_failure=True):
        self.process_runner(command, working_dir, subprocess_logger, exit_on_failure)[0]

    def start_datastream(self):
        logger.debug("*We* are the datastream vm." )

    def start_computing_environment(self):
        logger.warn("Cannot start computing environment from datastream vm, it must be started externally.")


    def configure_datastream(self, recommendation_partitions, zookeeper_hostport, config):
        """
        Configure the datastream vm for the upcoming task:
         * Create new topics if necessary
         * Increase the number of kafka topics, if necessary
        """
        if config.new_topic:
            topic_create_template = "/opt/apache/kafka/bin/kafka-topics.sh --zookeeper {zookeeper} --create --topic {topic} --partitions 1 --replication-factor 1"
            logger.info("Creating data topic ...")
            self.run_on_data_stream_manager(topic_create_template.format(zookeeper=zookeeper_hostport, topic=config.data_topic), exit_on_failure=True, capture_output=True)
            logger.info("Creating recommendation topic ...")
            self.run_on_data_stream_manager(topic_create_template.format(zookeeper=zookeeper_hostport, topic=config.recommendations_topic), exit_on_failure=True, capture_output=True)
        else:
            topic_info = "/opt/apache/kafka/bin/kafka-topics.sh --zookeeper {zookeeper} --topic recommendations --describe".format(zookeeper=zookeeper_hostport)
            result = self.run_on_data_stream_manager(topic_info, exit_on_failure=False, capture_output=True, default_relog_level='debug')
            num_partitions = len([str(line) for line in result if "Partition: " in str(line)])
            logger.debug("Detected number of partitions for 'recommendations' topic: " + str(num_partitions))
            if recommendation_partitions > num_partitions:
                logger.info("Setting the number of partitions of 'recommendation' topic to at least " + str(recommendation_partitions))
                topic_set = "/opt/apache/kafka/bin/kafka-topics.sh --alter --zookeeper {zookeeper_hostport} --topic {recommendations} --partitions {partitions} ".\
                                format(zookeeper_hostport=zookeeper_hostport, partitions=recommendation_partitions, recommendations=config.recommendations_topic)
                self.run_on_data_stream_manager(topic_set, default_relog_level='debug')
            else: logger.debug("Required num partitions " + str(recommendation_partitions) + ", so leaving it as it is.")


    def start(self, working_dir, subprocess_logger):
        self.execute(command=['vagrant', 'up'], working_dir=working_dir, subprocess_logger=subprocess_logger)

    def stop(self, working_dir, subprocess_logger):
        self.execute(command=['vagrant', 'halt'], working_dir=working_dir, subprocess_logger=subprocess_logger)
