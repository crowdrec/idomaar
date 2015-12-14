## INSTALL BASE SPARK ENV
cd /tmp
wget -nv -O spark.tgz http://d3kbcqa49mib13.cloudfront.net/spark-1.5.2-bin-hadoop2.6.tgz

tar -xvf spark.tgz
mkdir -p /opt/apache
mv spark-1.5.2-bin-hadoop2.6 /opt/apache
cd /opt/apache
ln -s /opt/apache/spark-1.5.2-bin-hadoop2.6 spark

cp /vagrant/vagrant/ipython/log4j.properties /opt/apache/spark/conf