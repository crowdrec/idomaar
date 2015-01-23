#!/bin/sh
java -cp KafkaOffsetMonitor-assembly-0.2.0.jar \
     com.quantifind.kafka.offsetapp.OffsetGetterWeb \
     --zk 192.168.22.5 \
     --port 8080 \
     --refresh 10.seconds \
     --retain 1.days
