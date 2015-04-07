import logging
import os
import subprocess
import sys

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

    def run_on_data_stream_manager(self, command, exit_on_failure=True, capture_output=False):
        """
        Run a command on the data stream manager VM. Returns the subprocess exit code.
        """
        command_list = command.split(" ")
        command_list.insert(0, "sudo")
        vagrant_command_string = ' '.join(command_list)
        logger.info("On data stream manager, executing command " + vagrant_command_string)
        result = self.execute_with_output(command=command_list, working_dir=self.datastream_manager_working_dir,
                                     subprocess_logger=datastream_logger, exit_on_failure=exit_on_failure)
        if capture_output: return result
        else: return result[0]

    def start_recommendation_manager(self, name, orchestrator_ip, recommendation_endpoint):
        """:param name: The name of the recommendation manager agent"""
        logger.info("Starting recommendation manager " + name)
        orchestrator_connection = "tcp://{ip_address}:{port}".format(ip_address=orchestrator_ip, port=self.orchestrator_port)
        recommendation_manager_start = ' '.join(["/vagrant/flume-config/startup/recommendation_manager-agent start", name, recommendation_endpoint, orchestrator_connection, str(self.recommendation_timeout_millis)])
        self.run_on_data_stream_manager(recommendation_manager_start)

    def stop_recommendation_manager(self, name):
        logger.info("Stopping recommendation manager " + name)
        recommendation_manager_stop = "/vagrant/flume-config/startup/recommendation_manager-agent stop " + name
        self.run_on_data_stream_manager(recommendation_manager_stop)

    def execute(self, command, working_dir, subprocess_logger, exit_on_failure=True):
        self.execute_with_output(command, working_dir, subprocess_logger, exit_on_failure)[0]

    def execute_with_output(self, command, working_dir, subprocess_logger, exit_on_failure):
        vagrant_command_string = ' '.join(command)
        process = subprocess.Popen(command, env=os.environ, cwd=working_dir, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=False)
        output_lines = list()
        while True:
            line = process.stdout.readline()
            if line:
                subprocess_logger.info(line.strip())
                output_lines.append(line)
            else: break
        exit_code = process.wait()
        if not exit_on_failure:
            output_lines.insert(0,exit_code)
            return output_lines
        if exit_code != 0:
            logger.error("Error occurred while executing {name} in directory {working_dir}, exit code is {code}. Exiting.".format(name=vagrant_command_string, working_dir=working_dir, code=exit_code))
            sys.exit(1)
        else: logger.info("Command '" + vagrant_command_string + "' is successful.")
        output_lines.insert(0,exit_code)
        return output_lines

    def start_datastream(self):
        logger.info("*We* are the datastream vm." )

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

        topic_info = "/opt/apache/kafka/bin/kafka-topics.sh --zookeeper {zookeeper} --topic recommendations --describe".format(zookeeper=zookeeper_hostport)
        result = self.run_on_data_stream_manager(topic_info, exit_on_failure=False, capture_output=True)
        num_partitions = len([str(line) for line in result if "Partition: " in str(line)])
        logger.info("Detected number of partitions for 'recommendations' topic: " + str(num_partitions))
        if recommendation_partitions > num_partitions:
            logger.info("Setting the number of partitions of 'recommendation' topic to at least " + str(recommendation_partitions))
            topic_set = "/opt/apache/kafka/bin/kafka-topics.sh --alter --zookeeper {zookeeper_hostport} --topic {recommendations} --partitions {partitions} ".\
                            format(zookeeper_hostport=zookeeper_hostport, partitions=recommendation_partitions, recommendations=config.recommendations_topic)
            self.run_on_data_stream_manager(topic_set)
        else: logger.info("Required num partitions " + str(recommendation_partitions) + ", so leaving it as it is.")


    def start(self, working_dir, subprocess_logger):
        self.execute(command=['vagrant', 'up'], working_dir=working_dir, subprocess_logger=subprocess_logger)

    def stop(self, working_dir, subprocess_logger):
        self.execute(command=['vagrant', 'halt'], working_dir=working_dir, subprocess_logger=subprocess_logger)
