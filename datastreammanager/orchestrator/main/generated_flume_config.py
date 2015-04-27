
import logging
import os

logger = logging.getLogger("flume-config-generator")

class FlumeConfig:

    def __init__(self, base_dir, template_file_name):
        self.base_dir = base_dir
        self.template_file_name = template_file_name
        template_config_file = os.path.join(base_dir, template_file_name)
        logger.debug("Reading template config file " + str(template_config_file))
        with open(template_config_file) as input_file:
            self.lines = input_file.readlines()

    def set_value(self, key, value):
        logger.debug("Setting {0} to {1}".format(key, value))
        self.lines.append(key + '=' + value + '\n')

    def generate(self, output_file_name):
        generated_config_dir = os.path.join(self.base_dir, 'generated')
        if not os.path.exists(generated_config_dir):
            os.makedirs(generated_config_dir)
        if output_file_name is None: output_file_name = self.template_file_name
        generated_config_file = os.path.join(generated_config_dir, output_file_name)
        logger.debug("Writing generated config file to " + str(os.path.abspath(generated_config_file)))
        with open(generated_config_file,'w') as output_file:
            for line in self.lines: output_file.write(line)
