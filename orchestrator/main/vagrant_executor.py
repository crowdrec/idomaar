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

    def run_on_data_stream_manager(self, command, exit_on_failure=True):
        """
        Run a command on the data stream manager VM. Returns the subprocess exit code.
        """
        vagrant_command = ["vagrant", "ssh", "-c", "sudo " + command]
        vagrant_command_string = ' '.join(vagrant_command)
        logger.info("On data stream manager, executing command " + vagrant_command_string)
        self.execute(command=vagrant_command, working_dir=self.datastream_manager_working_dir,
                                     subprocess_logger=datastream_logger, exit_on_failure=exit_on_failure)

    def start_recommendation_manager(self, name):
        """:param name: The name of the recommendation manager agent"""
        logger.info("Starting recommendation manager " + name)
        recommendation_manager_start = "/vagrant/flume-config/startup/recommendation_manager-agent start " + self.reco_engine_hostport + " " + \
                                       str(self.orchestrator_port) + " " + name
        self.run_on_data_stream_manager(recommendation_manager_start)

    def stop_recommendation_manager(self, name):
        logger.info("Stopping recommendation manager " + name)
        recommendation_manager_stop = "/vagrant/flume-config/startup/recommendation_manager-agent stop"
        self.run_on_data_stream_manager(recommendation_manager_stop)

    def execute(self, command, working_dir, subprocess_logger, exit_on_failure=True):
        vagrant_command_string = ' '.join(command)
        process = subprocess.Popen(command, env=os.environ, cwd=working_dir, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=False)
        while True:
            line = process.stdout.readline()
            if line: subprocess_logger.info(line.strip())
            else: break
        exit_code = process.wait()
        if not exit_on_failure: return exit_code
        if exit_code != 0:
            logger.error("Error occurred while executing {name} in directory {working_dir}, exit code is {code}. Exiting.".format(name=vagrant_command_string, working_dir=working_dir, code=exit_code))
            sys.exit(1)
        else: logger.info("Command '" + vagrant_command_string + "' is successful.")
        return exit_code

    def start_datastream(self):
        logger.info("DO: starting data stream")
        return self.start(working_dir=self.datastream_manager_working_dir, subprocess_logger=datastream_logger)

    def start(self, working_dir, subprocess_logger):
        self.execute(command=['vagrant', 'up'], working_dir=working_dir, subprocess_logger=subprocess_logger)

    def stop(self, working_dir, subprocess_logger):
        self.execute(command=['vagrant', 'halt'], working_dir=working_dir, subprocess_logger=subprocess_logger)
