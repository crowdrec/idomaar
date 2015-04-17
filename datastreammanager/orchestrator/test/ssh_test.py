import local_executor
from local_executor import LocalExecutor
import logging


logging.basicConfig(level='DEBUG')

executor = LocalExecutor("", 12, ".", 1000)

command = ' '.join(["ssh", "vagrant@192.168.22.201", "ls -la"])

executor.start_on_data_stream_manager(command=command, process_name="splitting", exit_on_failure=False)

#executor.process_runner(command, ".", logging.root, exit_on_failure=False, default_relog_level='info')