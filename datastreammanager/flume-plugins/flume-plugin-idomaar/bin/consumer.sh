#!/bin/sh

/opt/apache/kafka/bin/kafka-console-consumer.sh --zookeeper localhost:2181 --topic relations --from-beginning
