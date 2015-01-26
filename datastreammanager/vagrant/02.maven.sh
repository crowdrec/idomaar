#!/bin/sh

cd /tmp
wget -nv https://archive.apache.org/dist/maven/maven-3/3.2.3/binaries/apache-maven-3.2.3-bin.tar.gz
mkdir -p /opt/apache
cd /opt/apache/
tar -xvf /tmp/apache-maven-3.2.3-bin.tar.gz

export PATH=/opt/apache/apache-maven-3.2.3/bin:$PATH

su vagrant -c "echo 'export PATH=/opt/apache/apache-maven-3.2.3/bin:$PATH' >> ~/.bashrc"

echo 'export PATH=/opt/apache/apache-maven-3.2.3/bin:$PATH' >> ~/.bashrc


