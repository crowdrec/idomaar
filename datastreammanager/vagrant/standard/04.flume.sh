#!/bin/sh -Eux

cd /tmp
wget -nv -O flume.tgz http://apache.panu.it/flume/1.5.2/apache-flume-1.5.2-bin.tar.gz

tar -xvf flume.tgz
mkdir -p /opt/apache
mv apache-flume-1.5.2-bin /opt/apache
cd /opt/apache
ln -s /opt/apache/apache-flume-1.5.2-bin flume

