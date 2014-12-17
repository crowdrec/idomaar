#!/bin/sh -Eux

cd /tmp
wget -nv -O kafka.tgz http://mirror.nohup.it/apache/kafka/0.8.1.1/kafka_2.10-0.8.1.1.tgz

tar -xvf kafka.tgz
mkdir -p /opt/apache
mv kafka_2.10-0.8.1.1 /opt/apache
cd /opt/apache
ln -s /opt/apache/kafka_2.10-0.8.1.1 kafka

useradd kafka

cp /vagrant/vagrant/cloudera/init.d/kafka /etc/init.d/
chmod +x /etc/init.d/kafka

service kafka start
update-rc.d kafka defaults

