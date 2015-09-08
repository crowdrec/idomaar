## INSTALL BASE SPARK STREAMING ENV
#apt-get -y install spark-master hive

## INSTALL SCALA SBT
echo "deb https://dl.bintray.com/sbt/debian /" | sudo tee -a /etc/apt/sources.list.d/sbt.list
sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 642AC823
sudo apt-get update
sudo apt-get -y install sbt

# COMPILE SPARK STREAMING
cd /vagrant/evaluator/spark-streaming
sudo sbt publish-local

# TODO AFTER COMPILATION UPDATE AND SCALA HOME HAS TO BE REMOVED FROM BUILD SBT
# 