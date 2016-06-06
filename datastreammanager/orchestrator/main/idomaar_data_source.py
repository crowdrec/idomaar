import os
from urlparse import urlparse

import logging
logger = logging.getLogger()


class IdomaarDataSource:

    def __init__(self, location):
        self.location = location
        parsed_url = urlparse(location)
        if parsed_url.scheme:
            self.url = location
            self.file_name = None
        else:
            self.url = None
            self.file_name = '/vagrant/input/' + location
        self.format = self.guess_format(location)
        logger.info("Guessed file format is " + self.format)

    def guess_format(self, location):
        if location.endswith('.gz') or location.endswith('.gzip'): return 'gzip'
        else: return 'plain'

    def check_environment(self):
        pass

    def is_s3(self):
        return self.location.startswith('s3://')

    def check(self):
        self.check_file_exists()

    def check_file_exists(self):
        if not self.file_name:
            logger.debug("No file specified, nothing to check.")
            return
        target_file = self.file_name
        if os.path.exists(target_file):
            logger.debug("File {0} exists".format(target_file))
            return
        logger.info("File {0} not found, trying to convert to Unix path.".format(target_file))
        new_target_file = target_file.replace('\\', "/")
        if os.path.exists(new_target_file):
            logger.info("File {0} exists".format(new_target_file))
        else:
            raise Exception("File " + target_file + " not found. Please place your input files into the  datastreammanger/input folder and reference them " + \
                            " via the relative path.")


    def __str__(self):
        return "file_name: {0}, url: {1}, format {2}".format(self.file_name, self.url, self.format)

    def __repr__(self):
        return self.__str__()
