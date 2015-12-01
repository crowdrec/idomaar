#!/bin/sh -Eux

cd /tmp
wget -nv -O zookeeper.tgz http://www.eu.apache.org/dist/zookeeper/stable/zookeeper-3.4.6.tar.gz

tar -xvf zookeeper.tgz
mkdir -p /opt/zookeeper
mv zookeeper-3.4.6 /opt/apache
cd /opt/apache
ln -s /opt/apache/zookeeper-3.4.6 zookeeper

cp /vagrant/vagrant/cloudera/init.d/zookeeper-server /etc/init.d/
cp /opt/apache/zookeeper/conf/zoo_sample.cfg /opt/apache/zookeeper/conf/zoo.cfg 



mkdir /var/log/

useradd kafka
chown kafka:kafka /var/log/kafka
chown -R kafka:kafka /opt/apache/kafka
chown -R kafka:kafka /opt/apache/kafka_2.10-0.8.2.1

IP=$(ifconfig  | grep 'inet addr:'| grep 168 | grep 192|cut -d: -f2 | awk '{ print $1}')
#sed 's/broker.id=0/'broker.id=$1'/' /opt/apache/kafka/config/server.properties > /tmp/prop1.tmp
#sed 's/log.dirs=\/tmp\/kafka-logs/'log.dirs=\\/var\\/log\\/kafka'/' /opt/apache/kafka/config/server.properties > /tmp/prop1.tmp
sed 's/#advertised.host.name=<hostname routable by clients>/'advertised.host.name=$IP'/' /opt/apache/kafka/config/server.properties  > /tmp/prop2.tmp
sed 's/num\.partitions=2/num\.partitions=1/' /tmp/prop2.tmp > /tmp/prop3.tmp
sed 's/#host.name=localhost/'host.name=$IP'/' /tmp/prop3.tmp  > /opt/apache/kafka/config/server-vagrant.properties

chmod +x /etc/init.d/kafka

service kafka start
update-rc.d kafka defaults 98







