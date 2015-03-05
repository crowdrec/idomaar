import logging
import os
import sys
from orchestrator import Orchestrator
from test_executor import TestExecutor

orchestrator = Orchestrator(executor=TestExecutor(), datastreammanager = "test",
                            computing_env = "test",  training_uri = "train", test_uri = "test")

basedir = os.path.abspath("../../")
orchestrator.datastreammanager = os.path.join(basedir, "datastreammanager")

def test_output_from_commands():
    return orchestrator._run_on_data_stream_manager('ls -la')

def check_return_code():
    orchestrator._exit_on_failure("test_operation", test_output_from_commands())

def test_run():
    try:
        orchestrator.run()
    except Exception:
        logging.exception("Exception occurred, exiting.")
        orchestrator.close()
        os._exit(-1)

if __name__ == "__main__":
    logging.basicConfig(level = "INFO")
    # test_output_from_commands()
    # check_return_code()
    test_run()
