import os
import sys
 
spark_home = '/usr/lib/spark/'
sys.path.insert(0, os.path.join(spark_home, 'python'))
sys.path.insert(0, os.path.join(spark_home, 'python/lib/py4j-0.8.1-log4j-kafka-source.zip'))
execfile(os.path.join(spark_home, 'python/pyspark/shell.py'))
