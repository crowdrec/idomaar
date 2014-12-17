cd /tmp
wget http://archive.cloudera.com/cdh5/one-click-install/trusty/amd64/cdh5-repository_1.0_all.deb
dpkg -i cdh5-repository_1.0_all.deb

apt-get update
apt-get -y install flume-ng zookeeper-server

# INIT ZOOKEEPER
/etc/init.d/zookeeper-server init

# START ZOOKEEPER AND ENABLE AT BOOT
service zookeeper-server start
update-rc.d zookeeper-server enable

