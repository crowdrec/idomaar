import logging
import os

logger = logging.getLogger("recommendation_manager")

class RecommendationManager:
    """Proxy for the recommendation manager agent in the orchestrator."""

    def __init__(self, name, executor, config_base_dir):
        """
        :param name: the name, a unique identifier, for this recommendation manager agent
        :param executor: the executor for actual command execution
        """
        self.config_base_dir = config_base_dir
        self.name = name
        self.executor = executor

    def start(self, orchestrator_ip, recommendation_endpoint):
        self.executor.start_recommendation_manager(self.name, orchestrator_ip, recommendation_endpoint)

    def stop(self):
        self.executor.stop_recommendation_manager(self.name)

    def create_configuration(self, recommendation_target):
        """
        :param recommendation_target: The target where recommendation results are written.
        Possible prefixes are fs:, s3:, hdfs: .
        Use fs: to write to a directory of the local filesystem, for instance fs:/tmp/recommendations will instruct the agent
        to write recommendations to the /tmp/recommendations directory on the local filesystem.
        :return:
        """
        parts = recommendation_target.split(':', 1)
        type = parts[0]
        location = parts[1]
        logger.info("Recommendation target type {0} location {1} ".format(type, location))
        if type == "fs":
            template_config_file = os.path.join(self.config_base_dir, 'kafka_recommendations-TO-fs.conf')

        logger.info("Reading template config file " + str(template_config_file))
        with open(template_config_file) as input_file:
            config = input_file.readlines()

        if type == "fs":
            config.append("a1.sinks.fs.sink.directory = " + location)

        generated_config_dir = os.path.join(self.config_base_dir, 'generated')
        if not os.path.exists(generated_config_dir):
            os.makedirs(generated_config_dir)
        generated_config_file = os.path.join(generated_config_dir, 'kafka_recommendations_generated.conf')
        logger.info("Writing generated config file to " + str(os.path.abspath(generated_config_file)))
        with open(generated_config_file,'w') as output_file:
            for line in config: output_file.write(line)


