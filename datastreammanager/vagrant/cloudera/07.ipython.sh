apt-get -y install spark-python ipython-notebook python-pip python-dev python-numpy
#pip install pyspark
pip install runipy

useradd ipython
mkdir /home/ipython
chown ipython:ipython /home/ipython

su - ipython
cd
ipython profile create pyspark

cp /vagrant/vagrant/cloudera/ipython/00-pyspark-setup.py .ipython/profile_pyspark/startup
cp /vagrant/vagrant/cloudera/ipython/ipython_notebook_config.py .ipython/profile_pyspark/

cp /vagrant/vagrant/cloudera/ipython/start-ipython.sh /home/ipython
cp /vagrant/vagrant/cloudera/ipython/log4j.properties /etc/spark/conf
#chmod +x start-ipython.sh

#todo
# change info to warn in log4j conf in /etc/spark (copy the template file)

touch ~/.bashrc
echo 'PYTHONPATH=/usr/lib/spark/python/:/usr/lib/spark/python/build/:$PYTHONPATH' >> ~/.bashrc

