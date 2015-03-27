#!/bin/sh


cd
ipython profile create pyspark

cp /vagrant/scripts/00-pyspark-setup.py /home/ipython/.ipython/profile_pyspark/startup
cp /vagrant/scripts/ipython_notebook_config.py /home/ipython/.ipython/profile_pyspark/

cp /vagrant/scripts/start-ipython.sh /home/ipython/
#cp /vagrant/scripts/log4j.properties /etc/spark/conf
chmod +x start-ipython.sh

touch ~/.bashrc
echo 'PYTHONPATH=/usr/lib/spark/python/:/usr/lib/spark/python/build/:$PYTHONPATH' >> ~/.bashrc

## copy notebooks
cp /vagrant/notebooks/* /home/ipython

