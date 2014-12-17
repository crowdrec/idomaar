cd /vagrant/flume-plugins/flume-plugin-idomaar
mvn clean package

# INSTALL IDOMAAR PLUGIN IN FLUME LIB DIRECTORY
cp target/flume-plugin-idomaar-*.jar /usr/lib/flume-ng/lib

