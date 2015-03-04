

class TestExecutor():

    def __init__(self):
        self.reco_engine_hostport='192.168.22.100:5560'
        self.orchestrator_port=2761,
        self.datastream_manager_working_dir="datastreammanager"  #os.path.join(basedir, "datastreammanager")
        self.recommendation_timeout_millis=4000

    def start(self, working_dir, subprocess_logger): pass

    def start_datastream(self): pass

    def configure_datastream(self, num_concurrent_recommendation_managers, zookeeper_hostport): pass
