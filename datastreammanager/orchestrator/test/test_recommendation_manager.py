import logging
from recommendation_manager import RecommendationManager



def test_config_generation():

    manager = RecommendationManager(name="test", executor=None, config_base_dir='../../flume-config/config')
    manager.create_configuration(recommendation_target="fs:/tmp/recommendations")

if __name__ == "__main__":
    logging.basicConfig(level = "INFO")
    test_config_generation()

