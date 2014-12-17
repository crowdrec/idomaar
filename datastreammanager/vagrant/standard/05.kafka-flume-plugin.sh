# SINCE FLUME 1.6 KAFKA SINK WILL BE INCLUDED IN FLUME DISTRIBUTION

apt-get install unzip
cd /tmp

git clone https://github.com/thilinamb/flume-ng-kafka-sink.git

cd flume-ng-kafka-sink

/opt/apache/apache-maven-3.2.3/bin/mvn clean install -DskipTests

mkdir 	-p /opt/apache/flume/plugins.d/
cd 		/opt/apache/flume/plugins.d/
unzip /tmp/flume-ng-kafka-sink/dist/target/flume-kafka-sink-dist-0.5.0-bin.zip
