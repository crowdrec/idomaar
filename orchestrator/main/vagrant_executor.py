import logging
import os
import subprocess
import sys

logger = logging.getLogger("orchestrator:execute")
datastream_logger = logging.getLogger("datastream")

class VagrantExecutor:
    """
    Run vagrant commands to actually execute operations initiated by the orchestrator.
    """

    def __init__(self, reco_engine_hostport, orchestrator_port, datastream_manager_working_dir):
        """
        :param reco_engine_hostport: host and port of the recommendation engine
        :param orchestrator_port: used by the recommendation manager agent
        """
        self.orchestrator_port = orchestrator_port
        self.reco_engine_hostport = reco_engine_hostport
        self.datastream_manager_working_dir = datastream_manager_working_dir

    def run_on_data_stream_manager(self, command, exit_on_failure=True, capture_output=False):
        """
        Run a command on the data stream manager VM. Returns the subprocess exit code.
        """
        vagrant_command = ["vagrant", "ssh", "-c", "sudo " + command]
        vagrant_command_string = ' '.join(vagrant_command)
        logger.info("On data stream manager, executing command " + vagrant_command_string)
        result = self.execute_with_output(command=vagrant_command, working_dir=self.datastream_manager_working_dir,
                                     subprocess_logger=datastream_logger, exit_on_failure=exit_on_failure)
        if capture_output: return result
        else: return result[0]

    def start_recommendation_manager(self, name):
        """:param name: The name of the recommendation manager agent"""
        logger.info("Starting recommendation manager " + name)
        recommendation_manager_start = "/vagrant/flume-config/startup/recommendation_manager-agent start " + name + " " + self.reco_engine_hostport + " " + str(self.orchestrator_port)
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
        logger.info("DO: starting data stream")
        return self.start(working_dir=self.datastream_manager_working_dir, subprocess_logger=datastream_logger)

    def configure_datastream(self, recommendation_partitions):
        """
        Configure the datastream vm for the upcoming task:
         * Increase the number of kafka topics, if necessary
        """
        topic_info = "/opt/apache/kafka/bin/kafka-topics.sh --zookeeper localhost:2181 --topic recommendations --describe"
        result = self.run_on_data_stream_manager(topic_info, exit_on_failure=False, capture_output=True)
        num_partitions = len([str(line) for line in result if "Partition: " in str(line)])
        logger.info("Detected number of partitions for 'recommendations' topic: " + str(num_partitions))
        if recommendation_partitions > num_partitions:
            logger.info("Setting the number of partitions of 'recommendation' topic to at least " + str(recommendation_partitions))
            topic_set = "/opt/apache/kafka/bin/kafka-topics.sh --alter --zookeeper localhost:2181 --topic recommendations --partitions " + str(recommendation_partitions)
            self.run_on_data_stream_manager(topic_set)
        else: logger.info("Required num partitions " + str(recommendation_partitions) + ", so leaving it as it is.")


    def start(self, working_dir, subprocess_logger):
        self.execute(command=['vagrant', 'up'], working_dir=working_dir, subprocess_logger=subprocess_logger)

    def stop(self, working_dir, subprocess_logger):
        self.execute(command=['vagrant', 'halt'], working_dir=working_dir, subprocess_logger=subprocess_logger)
