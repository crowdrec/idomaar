#!/bin/sh -Eux

cd /opt/
git clone https://github.com/apache/flume.git
cd flume
git checkout origin/flume-1.6
mvn compile
mvn install

ln target /opt/apache/flume -s

