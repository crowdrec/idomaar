#!/bin/sh

/opt/apache/kafka/bin/kafka-console-producer.sh --broker-list localhost:9092,localhost:9093 --topic relations
