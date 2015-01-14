apt-get -y install spark-python ipython-notebook python-pip python-dev python-numpy
pip install pyspark
useradd ipython
mkdir /home/ipython
chown ipython:ipython

su - ipython
python profile create pyspark

cp /vagrant/vagrant/cloudera/ipython/00-pyspark-setup.py .ipython/profile_pyspark/startup
cp /vagrant/vagrant/cloudera/ipython/ipython_notebook_config.py .ipython/profile_pyspark/

cp /vagrant/vagrant/cloudera/ipython/start-ipython.sh /home/ipython
chmod +x start-ipython.sh

#todo
# change info to warn in log4j conf in /etc/spark (copy the template file)