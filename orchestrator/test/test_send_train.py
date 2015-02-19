import os
from orchestrator import Orchestrator
from mock_computing_environment import MockComputingEnvironment

ORCHESTRATOR_ZMQ_SERVER_PORT = 2728

orchestrator = Orchestrator(port=ORCHESTRATOR_ZMQ_SERVER_PORT)
basedir = os.path.abspath("../../")
orchestrator.datastreammanager = os.path.join(basedir, "datastreammanager")
orchestrator.training_uri = "https://raw.githubusercontent.com/crowdrec/datasets/master/01.MovieTweetings/datasets/snapshots_10K/evaluation/training/data.dat"

def test_output_from_commands():
    return orchestrator._run_on_data_stream_manager('ls -la')

def check_return_code():
    orchestrator._exit_on_failure("test_operation", test_output_from_commands())

def test_send_train():
    orchestrator.send_train()


if __name__ == "__main__":
    # test_output_from_commands()

    computing_environment = MockComputingEnvironment(computing_environment_port=2729, orchestrator_port=ORCHESTRATOR_ZMQ_SERVER_PORT)
    computing_environment.send_ready_message()

    print("WAIT: waiting for new message")
    message = orchestrator._socket.recv_multipart()
    print("0MQ: received message: %s " % message)
    test_send_train()


