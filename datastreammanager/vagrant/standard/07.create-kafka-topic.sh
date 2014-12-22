
/opt/apache/kafka/bin/kafka-topics.sh --zookeeper localhost:2181 --create --topic data  --partitions 1 --replication-factor 1
/opt/apache/kafka/bin/kafka-topics.sh --zookeeper localhost:2181 --create --topic recommendations  --partitions 1 --replication-factor 1
