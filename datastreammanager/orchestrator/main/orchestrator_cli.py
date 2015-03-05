import logging
import os
import colorlog
from plumbum import cli
import sys
from local_executor import LocalExecutor
from orchestrator import Orchestrator
from vagrant_executor import VagrantExecutor

logger = logging.getLogger("orchestrator")

class OrchestratorCli(cli.Application):

    PROGNAME = "orchestrator"
    VERSION = "0.0.1"

    host_orchestrator = cli.Flag(["host-orchestrator"], help = "If given, the orchestrator assumes to be running on the host OS, and execute all datastream commands via vagrant."+
        " The default assumption is that the orchestrator is running on the same (virtual) box as the datastream components (hence doesn't have to go via vagrant)." )

    comp_env = None

    @cli.switch("--comp-env-dir", str)
    def comp_env(self, directory):
        """The relative path to the computing environment vagrant directory. This only makes sense if the orchestrator runs on the same host as the computing environment."""
        self.comp_env = directory

    @cli.switch("--training-uri", str, mandatory=True)
    def training_uri(self, training_uri):
        """The location of the training data."""
        self.training_uri = training_uri

    @cli.switch("--test-uri", str, mandatory=True)
    def test_uri(self, test_uri):
        """The location of the test data."""
        self.test_uri = test_uri

    def main(self):
        # TODO RECOMMENDATION HOSTNAME MUST BE EXTRACTED FROM MESSAGES
        logger.info("Training data URI: %s" % self.training_uri)
        logger.info("Test data URI: %s" % self.test_uri)
        logger.info("Computing environment path: %s" % self.comp_env)
        basedir = os.path.abspath("../../")
        logger.info("Idomaar base path: %s" % basedir)

        if self.host_orchestrator:
            datastreammanager = os.path.join(basedir, "datastreammanager")
            computing_env_dir = os.path.join(basedir, "computingenvironments")
            executor = VagrantExecutor(reco_engine_hostport='192.168.22.100:5560', orchestrator_port=2761,
                                           datastream_manager_working_dir=datastreammanager, recommendation_timeout_millis=4000, computing_env_dir=computing_env_dir)
        else:
            logger.info("Using local executor.")
            datastreammanager = "/vagrant"
            executor = LocalExecutor(reco_engine_hostport='192.168.22.100:5560', orchestrator_port=2761,
                                               datastream_manager_working_dir=datastreammanager, recommendation_timeout_millis=4000)

        orchestrator = Orchestrator(executor=executor, datastreammanager = datastreammanager, training_uri = self.training_uri, test_uri = self.test_uri)
        try:
            orchestrator.run()
        except Exception:
            logger.exception("Exception occurred, hard shutdown.")
            os._exit(-1)

        # TODO: check if data stream channel is empty (http metrics)
        # TODO: test/evaluate the output

        #logger.info("DO: Stopping computing environment")
        #orchestrator.executor.stop(working_dir=orchestrator.computing_env, subprocess_logger=computing_environment_logger)

        logger.info("Finished.")

def setup_logging(logger_to_conf):
    logger_to_conf.setLevel("DEBUG")
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
    root_logger = logging.getLogger()
    setup_logging(root_logger)
    OrchestratorCli.run()