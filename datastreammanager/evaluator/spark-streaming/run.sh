#!/bin/sh
cd /vagrant/evaluator/spark-streaming
#sbt "run spark://vagrant-ubuntu-trusty-64:7077 $1 localhost:2181"

sbt "run local[2] $1 192.168.22.5:2181"
