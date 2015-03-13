import httplib
import logging
import requests
from orchestrator_exceptions import TimeoutException

logger = logging.getLogger("computing-environment-http")

class HttpComputingEnvironmentProxy:
    """A class capable of communicating with a computing environment over HTTP."""

    def __init__(self, address):
        self.address = address

    def connect(self, timeout_secs):
        #self.comp_env_socket.connect(self.address)
        #logger.info("Connected to " + self.address)
        #logger.info("Waiting at most {secs} secs for computing environment to get ready ...".format(secs=timeout_secs))
        try:
            message = self.respond(request="HELLO", timeout_millis=timeout_secs*1000)
        except Exception:
            logger.exception("Exception occurred")
            raise Exception("No answer from computing environment, probable timeout. Computing environment failed or didn't start in {secs} seconds.".format(secs=timeout_secs))
        if not message.startswith('READY'):
            raise Exception("Computing environment send message {0}, which is not READY.".format(message))

    def post(self, command, data, timeout_millis):
        post_address = self.address + "/" + command
        logger.info("POST to " + post_address)
        timeout_secs = timeout_millis / 1000 if timeout_millis is not None else None
        response = requests.post(post_address, timeout=timeout_secs)
        status_code = response.status_code
        logger.info("Received status code {0}, response {1}".format(status_code, response.text))
        if status_code != httplib.OK:
            raise "Computing environment indicated error, HTTP code {0)".format(status_code)
        return response.text

    def respond(self, request, timeout_millis=None):
        if type(request) is list:
            command = request[0]
            data = '\n'.join(request[1:])
        else:
            command = request
            data = ""
        response = self.post(command=command, data=data, timeout_millis=timeout_millis)
        return response

    def send_train(self, zookeeper_hostport, kafka_topic):
        train_message = ['TRAIN', zookeeper_hostport, kafka_topic]
        result = self.respond(train_message)
        lines = result.split('\n')
        logger.info("First lines of response are " + '\n'.join(lines[0:3]))
        status_code = lines[0]
        recommendation_endpoint = lines[1]
        logger.info("Status code {0}, recommendation endpoint {1}".format(status_code, recommendation_endpoint))
        return status_code, recommendation_endpoint

    def send_test(self):
        logger.info("Sending test message TEST and wait for response")
        return self.respond(request=['TEST'])

    def send_stop(self):
        logger.info("Sending STOP message to computing environment")
        return self.respond(request=['STOP'])

    def close(self):
        logger.info("ZMQ connection closing ...")
        self.comp_env_socket.close()
        self.context.term()
        logger.info("ZMQ connection closed.")
