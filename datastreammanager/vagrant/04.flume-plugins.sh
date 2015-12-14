#download and install flume-ng
cd /tmp
wget -nv -O flume.tgz http://mirror.nohup.it/apache/flume/1.6.0/apache-flume-1.6.0-bin.tar.gz

tar -xvf flume.tgz
mkdir -p /opt/apache
sudo mv apache-flume-1.6.0-bin/ /opt/apache/
cd /opt/apache
ln -s /opt/apache/apache-flume-1.6.0-bin/ flume

mkdir -p /var/log/flume-ng

cd /vagrant/flume-plugins/flume-plugin-idomaar
/opt/apache/apache-maven-3.2.3/bin/mvn clean install

# INSTALL IDOMAAR PLUGIN IN FLUME DIRECTORY
mkdir -p /opt/apache/flume/plugins.d/idomaar/lib
mkdir -p /opt/apache/flume/plugins.d/idomaar/libext

cp target/flume-plugin-idomaar-*.jar /opt/apache/flume/plugins.d/idomaar/lib
cp target/lib/*jar /opt/apache/flume/plugins.d/idomaar/libext

useradd flume

### COPY ENVIRONMENT CONFIGURATION 
sudo ln /opt/apache/zookeeper/zookeeper-3.4.6.jar /opt/apache/flume/lib -s


# INSTALL PATCHED KAFKA PLUGIN, RESOLVE ERROR IN PARTITION KEY
#cd /vagrant/flume-plugins/flume-kafka-source
#/opt/apache/apache-maven-3.2.3/bin/mvn clean install

#rm /usr/lib/flume-ng/lib/flume-kafka-source-1.5.0-cdh5.3.0.jar
#cp target/flume-kafka-source-1.5.0-cdh5.3.0.jar /usr/lib/flume-ng/lib/flume-kafka-source-1.5.0-cdh5.3.0.jar