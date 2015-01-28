* Tested with Python 2.8
* Install (pip) pyzmq and enum34

* (Install ruby if required)

* Install vagrant
e.g., on debian-based env: sudo apt-get install vagrant

* Install git

* Install virtual box 

* run orchestrator
orchestrator.py computing_environment training_data_uri test_data_uri


e.g. python2.7 orchestrator.py 01.linux/01.centos/01.mahout/ https://raw.githubusercontent.com/crowdrec/datasets/master/01.MovieTweetings/datasets/snapshots_10K/evaluation/training/data.dat https://raw.githubusercontent.com/crowdrec/datasets/master/01.MovieTweetings/datasets/snapshots_10K/evaluation/test/data.dat


