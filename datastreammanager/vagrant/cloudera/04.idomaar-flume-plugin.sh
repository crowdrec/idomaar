cd /vagrant/flume-plugins/flume-plugin-idomaar
mvn clean install

# INSTALL IDOMAAR PLUGIN IN FLUME LIB DIRECTORY
cp target/flume-plugin-idomaar-*.jar /usr/lib/flume-ng/lib
cp /vagrant/flume-plugins/flume-plugin-idomaar/target/lib/jeromq-* /usr/lib/flume-ng/lib


