import logging
import os
try:
    import pwd
    import grp
except ImportError:
    print("No module pwd, grp. Probably running on Windows?")
    #import winpwd as pwd

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

    def set_value(self, config, key, value):
        config.append(key + '=' + value + '\n')

    def create_configuration(self, recommendation_target, communication_protocol, recommendations_topic, recommendation_results_topic, kafka_hostport):
        """
        :param recommendation_target: The target where recommendation results are written.
        :param communication_protocol: tcp or http
        Possible prefixes are fs:, s3:, hdfs: .
        Use fs: to write to a directory of the local filesystem, for instance fs:/tmp/recommendations will instruct the agent
        to write recommendations to the /tmp/recommendations directory on the local filesystem.
        :return:
        """
        parts = recommendation_target.split(':', 1)
        target_type = parts[0]
        location = parts[1]
        logger.info("Recommendation target type {0} location {1}; creating config with communication protocol {2}".format(target_type, location, communication_protocol))
        if target_type == "fs":
            template_config_file = os.path.join(self.config_base_dir, 'kafka_recommendations-TO-fs.conf')
        elif target_type == "hdfs":
            template_config_file = os.path.join(self.config_base_dir, 'kafka_recommendations-TO-hdfs.conf')

        logger.debug("Reading template config file " + str(template_config_file))
        with open(template_config_file) as input_file:
            config = input_file.readlines()

        if target_type == "fs":
            if not os.path.exists(location):
                logger.debug("{0} doesn't exist, creating it and chown to flume".format(location))
                os.makedirs(location)
                os.chown(location, pwd.getpwnam("flume").pw_uid, grp.getgrnam("flume").gr_gid)
            self.set_value(config, "a1.sinks.fs.sink.directory", location)
        elif target_type == "hdfs":
            self.set_value(config, "a1.sinks.hdfs.hdfs.path", location)

        if communication_protocol == 'tcp':
            self.set_value(config, 'a1.sources.r1.interceptors.i1.type', 'eu.crowdrec.flume.plugins.interceptor.IdomaarRecommendationInterceptor$Builder')
        elif communication_protocol == 'http':
            self.set_value(config, 'a1.sources.r1.interceptors.i1.type', 'eu.crowdrec.flume.plugins.interceptor.IdomaarHTTPRecommendationInterceptor$Builder')
        else: raise "Recommendation manager communication protocol must be either tcp or http."

        self.set_value(config, 'a1.sources.r1.topic', recommendations_topic)
        self.set_value(config, 'a1.sinks.kafka_sink.topic', recommendation_results_topic)
        self.set_value(config, 'a1.sinks.kafka_sink.brokerList', kafka_hostport)

        generated_config_dir = os.path.join(self.config_base_dir, 'generated')
        if not os.path.exists(generated_config_dir):
            os.makedirs(generated_config_dir)
        generated_config_file = os.path.join(generated_config_dir, 'kafka_recommendations_generated.conf')
        logger.debug("Writing generated config file to " + str(os.path.abspath(generated_config_file)))
        with open(generated_config_file,'w') as output_file:
            for line in config: output_file.write(line)