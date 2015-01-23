cd /vagrant/flume-plugins/flume-plugin-idomaar
mvn clean install

# INSTALL IDOMAAR PLUGIN IN FLUME LIB DIRECTORY
cp target/flume-plugin-idomaar-*.jar /usr/lib/flume-ng/lib
cp /vagrant/flume-plugins/flume-plugin-idomaar/target/lib/jeromq-* /usr/lib/flume-ng/lib


# INSTALL PATCHED KAFKA PLUGIN
cd /vagrant/flume-plugins/flume-kafka-source
mvn clean install
rm /usr/lib/flume-ng/lib/flume-kafka-source-1.5.0-cdh5.3.0.jar
cp target/flume-kafka-source-1.5.0-cdh5.3.0.jar /usr/lib/flume-ng/lib/flume-kafka-source-1.5.0-cdh5.3.0.jar