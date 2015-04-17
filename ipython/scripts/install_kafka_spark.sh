#!/bin/bash
apt-get install ivy
mkdir -p /usr/share/ivy/cache
java -jar /usr/share/java/ivy.jar -cache /usr/share/ivy/cache -ivy /vagrant/scripts/kafka-spark-ivy.xml -cachepath /usr/share/ivy/path.txt
