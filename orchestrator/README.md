
Tested with Python 2.79

Install python	https://www.python.org/downloads/release/python-279/
(on Windows, remember to set Python Path https://docs.python.org/2/using/windows.html)

Install pip (included with Python 2.79)

Install pyzmq and enum34 via pip (go to pip dir, type pip enum34 and pip pyzmq)

(Install ruby if required)

Install vagrant e.g., 
(on debian-based env: sudo apt-get install vagrant 
on Windows/MacOs https://www.vagrantup.com/downloads.html)

Install git
(http://git-scm.com/downloads)

Use git to clone this repository
(e.g. git clone https://github.com/crowdrec/idomaar)

Install virtual box
(in windows, REMEMBER to set the path my computer -> properties -> advanced -> under advanced tab click enviroment variable -> new name: Vbox Value: C:\Program Files\Oracle\VirtualBox)

run orchestrator orchestrator.py computing_environment training_data_uri test_data_uri

e.g. python2.7 orchestrator.py 01.linux/01.centos/01.mahout/ https://raw.githubusercontent.com/crowdrec/datasets/master/01.MovieTweetings/datasets/snapshots_10K/evaluation/training/data.dat https://raw.githubusercontent.com/crowdrec/datasets/master/01.MovieTweetings/datasets/snapshots_10K/evaluation/test/data.dat
