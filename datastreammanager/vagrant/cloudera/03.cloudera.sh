cd /tmp
wget http://archive.cloudera.com/cdh5/one-click-install/trusty/amd64/cdh5-repository_1.0_all.deb
dpkg -i cdh5-repository_1.0_all.deb

apt-get update
#apt-get -y install flume-ng
apt-get -y install zookeeper-server
apt-get -y install python-pip

# INIT ZOOKEEPER
/etc/init.d/zookeeper-server init

# START ZOOKEEPER AND ENABLE AT BOOT
service zookeeper-server start
update-rc.d zookeeper-server enable


# REMOVE DEBUG OPTION IN FLUME-NG AGENT START
#sed -i 's/CLEAN_FLAG=1/CLEAN_FLAG=0/' /usr/lib/flume-ng/bin/flume-ng


