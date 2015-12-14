#!/bin/sh -Eux

cd /tmp
wget -nv -O zookeeper.tgz http://www.eu.apache.org/dist/zookeeper/stable/zookeeper-3.4.7.tar.gz

tar -xvf zookeeper.tgz
mkdir -p /opt/apache
mv zookeeper-3.4.7 /opt/apache
cd /opt/apache
ln -s /opt/apache/zookeeper-3.4.7 zookeeper

cp /vagrant/vagrant/init.d/zookeeper-server /etc/init.d/
cp /opt/apache/zookeeper/conf/zoo_sample.cfg /opt/apache/zookeeper/conf/zoo.cfg 
chmod +x /etc/init.d/zookeeper-server
mkdir /var/log/zookeeper

useradd zookeeper
chown -R zookeeper:zookeeper /opt/apache/zookeeper
chown -R zookeeper:zookeeper /opt/apache/zookeeper-3.4.7
chown -R zookeeper:zookeeper /var/log/zookeeper

service zookeeper-server start
update-rc.d zookeeper-server defaults 98







