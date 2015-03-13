import zmq
import logging
from orchestrator_exceptions import TimeoutException

logger = logging.getLogger("computing-environment-zmq")


class ZmqComputingEnvironmentProxy:
    """A class capable of communicating with a computing environment over ZMQ."""

    communication_protocol = "tcp"

    def __init__(self, address):
        self.address = address
        self.context = zmq.Context()
        self.comp_env_socket = self.context.socket(zmq.REQ)

    def connect(self, timeout_secs):
        self.comp_env_socket.connect(self.address)
        logger.info("Connected to " + self.address)
        logger.info("Waiting at most {secs} secs for computing environment to get ready ...".format(secs=timeout_secs))
        try:
            message = self.respond(request="HELLO", timeout_millis=timeout_secs*1000)
        except Exception:
            logger.exception("Exception occurred")
            raise Exception("No answer from computing environment, probable timeout. Computing environment failed or didn't start in {secs} seconds.".format(secs=timeout_secs))
        if message[0] != 'READY':
            raise Exception("Computing environment send message {0}, which is not READY.".format(message))

    def send_train(self, zookeeper_hostport, kafka_topic):
        # Pass to the orchestrator the zookeeper address and the name of the topics
        # THE FORMAT IS
        # MESSAGE, ZOOKEEPER URL, ENTITIES TOPIC, RELATIONS TOPIC
        train_message = ['TRAIN', zookeeper_hostport, kafka_topic]
        return self.respond(train_message)

    def send_test(self):
        logger.info("Sending test message TEST and wait for response")
        return self.respond(request=['TEST'])

    def send_stop(self):
        logger.info("Sending STOP message to computing environment")
        return self.respond(request=['STOP'])

    def respond(self, request, timeout_millis=None):
        if type(request) is list: self.comp_env_socket.send_multipart(request)
        else: self.comp_env_socket.send(request)
        poller = zmq.Poller()
        poller.register(self.comp_env_socket, zmq.POLLIN) # POLLIN for recv, POLLOUT for send
        logger.info("Sending request {0} to computing environment.".format(request))
        logger.info("Waiting {time} for computing environment to answer ...".format(time=str(timeout_millis / 1000) + " secs" if timeout_millis else "indefinitely"))
        poll_result = poller.poll(timeout_millis)
        if not poll_result:
            self.comp_env_socket.close()
            raise TimeoutException("No answer from computing environment, probable timeout.")
        message = self.comp_env_socket.recv_multipart()
        logger.info("Response from computing environment " + str(message))
        return message

    def close(self):
        logger.info("ZMQ connection closing ...")
        self.comp_env_socket.close()
        self.context.term()
        logger.info("ZMQ connection closed.")