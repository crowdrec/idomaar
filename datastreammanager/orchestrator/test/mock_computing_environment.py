import zmq

class MockComputingEnvironment:

    def __init__(self, computing_environment_port, orchestrator_port):
        self.orchestrator_port = orchestrator_port
        self.port = computing_environment_port
        self._context = zmq.Context()
        self._socket = self._context.socket(zmq.REQ)

    def send_ready_message(self):
        self._socket.bind("tcp://*:%s" % self.port)
        self._socket.connect("tcp://127.0.0.1:" + str(self.orchestrator_port))
        self._socket.send("READY")
