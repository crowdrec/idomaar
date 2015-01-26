#!/bin/sh
add-apt-repository -y ppa:webupd8team/java
apt-get -y update

apt-get install -y software-properties-common python-software-properties screen vim git wget

/bin/echo debconf shared/accepted-oracle-license-v1-1 select true | /usr/bin/debconf-set-selections
apt-get -y install oracle-java7-installer oracle-java7-set-default

export JAVA_HOME=/usr

su vagrant -c "touch ~/.bashrc"
su vagrant -c "echo 'export JAVA_HOME=/usr' >> ~/.bashrc"


echo 'export JAVA_HOME=/usr' >> ~/.bashrc