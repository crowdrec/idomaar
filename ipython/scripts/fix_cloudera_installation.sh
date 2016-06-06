#!/bin/sh
mkdir -p /usr/lib/zookeeper
mkdir -p /usr/lib/zookeeper/lib
ln -s -f /usr/lib/parquet/lib/slf4j-log4j12-1.7.5.jar /usr/lib/zookeeper/lib/slf4j-log4j12.jar
