cd /vagrant/flume-plugins/flume-plugin-idomaar
mvn clean package


mkdir 	-p /opt/apache/flume/plugins.d/
mkdir 	-p /opt/apache/flume/plugins.d/idomaar-source
mkdir 	-p /opt/apache/flume/plugins.d/idomaar-source/lib

cp target/flume-plugin-idomaar-*.jar /opt/apache/flume/plugins.d/idomaar-source/lib


