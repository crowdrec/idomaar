#!/bin/sh -Eux

# INSTALL HADOOP JAR IN ORDER TO BE ABLE TO USE HDFS SINK FOR FLUME

cd /tmp
#wget -nv http://apache.panu.it/hadoop/core/hadoop-1.2.1/hadoop_1.2.1-1_x86_64.deb
wget -nv -O hadoop.tgz http://mirrors.muzzy.it/apache/hadoop/common/hadoop-1.2.1/hadoop-1.2.1.tar.gz
tar xvfz hadoop.tgz
mv hadoop-1.2.1/ /opt/apache/
ln /opt/apache/hadoop-1.2.1/ /opt/apache/hadoop -ls


# COPY DEPENDENCY FOR S3HDFS
cp /usr/share/hadoop/hadoop-core-1.2.1.jar /opt/apache/flume/lib/

cp /opt/apache/hadoop-1.2.1/lib/commons-configuration-1.6.jar lib/
cp /opt/apache/hadoop-1.2.1/lib/jets3t-0.6.1.jar lib
cp /opt/apache/hadoop-1.2.1/lib/commons-httpclient-3.0.1.jar lib/
