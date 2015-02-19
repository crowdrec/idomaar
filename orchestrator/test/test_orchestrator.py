import os
from orchestrator import Orchestrator

orchestrator = Orchestrator()
basedir = os.path.abspath("../../")
orchestrator.datastreammanager = os.path.join(basedir, "datastreammanager")

def test_output_from_commands():
    return orchestrator._run_on_data_stream_manager('ls -la')

def check_return_code():
    orchestrator._exit_on_failure("test_operation", test_output_from_commands())


if __name__ == "__main__":
    # test_output_from_commands()
    check_return_code()
