
/opt/apache/kafka/bin/kafka-topics.sh --zookeeper localhost:2181 --create --topic relations  --partitions 1 --replication-factor 1
/opt/apache/kafka/bin/kafka-topics.sh --zookeeper localhost:2181 --create --topic entities  --partitions 1 --replication-factor 1
