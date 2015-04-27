
class IdomaarEnvironment(object):
    
    orchestrator_ip = None
    
    kafka_hostport = None
    zookeeper_hostport = None
    
    comp_env_address = None
    
    input_port = None
    input_topic = None
    
    recommendation_requests_topic = None
    recommendation_results_topic = None
    ground_truth_topic = None
    
    evaluator_ip = None
    
    def validate(self):
        assert self.orchestrator_ip is not None
        assert self.kafka_hostport is not None
        assert self.zookeeper_hostport is not None
        assert self.comp_env_address is not None
        assert self.evaluator_ip is not None
#         if (self.input_topic is not None) != (self.input_hostport is not None):
#             raise "Exactly one of input_topic and input_hostport must be specified. Input topic: " + str(self.input_topic) + ", input hostport " + str(self.input_hostport)
        assert self.recommendation_requests_topic is not None
        assert self.ground_truth_topic is not None
        
    def printed_form(self):
        return str(self.__dict__)
        
    
        