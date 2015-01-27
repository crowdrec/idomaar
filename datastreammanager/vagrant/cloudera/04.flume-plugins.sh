cd /vagrant/flume-plugins/flume-plugin-idomaar
/opt/apache/apache-maven-3.2.3/bin/mvn clean install

# INSTALL IDOMAAR PLUGIN IN FLUME LIB DIRECTORY
cp target/flume-plugin-idomaar-*.jar /usr/lib/flume-ng/lib
cp target/lib/jeromq-* /usr/lib/flume-ng/lib


# INSTALL PATCHED KAFKA PLUGIN, RESOLVE ERROR IN PARTITION KEY
cd /vagrant/flume-plugins/flume-kafka-source
/opt/apache/apache-maven-3.2.3/bin/mvn clean install

rm /usr/lib/flume-ng/lib/flume-kafka-source-1.5.0-cdh5.3.0.jar
cp target/flume-kafka-source-1.5.0-cdh5.3.0.jar /usr/lib/flume-ng/lib/flume-kafka-source-1.5.0-cdh5.3.0.jar