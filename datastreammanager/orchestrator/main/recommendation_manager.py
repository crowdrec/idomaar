

class RecommendationManager:
    """Proxy for the recommendation manager agent in the orchestrator."""

    def __init__(self, name, executor):
        """
        :param name: the name, a unique identifier, for this recommendation manager agent
        :param executor: the executor for actual command execution
        """
        self.name = name
        self.executor = executor

    def start(self):
        self.executor.start_recommendation_manager(self.name)

    def stop(self):
        self.executor.stop_recommendation_manager(self.name)







