cd /vagrant/flume-plugins/flume-plugin-idomaar
mvn clean compile assembly:single

# INSTALL IDOMAAR PLUGIN IN FLUME LIB DIRECTORY
cp target/flume-plugin-idomaar-*.jar /usr/lib/flume-ng/lib


