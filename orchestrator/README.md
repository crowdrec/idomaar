* Tested with Python 2.8
* Install (pip) pyzmq and enum34

* (Install ruby if required)

* Install vagrant
e.g., on debian-based env: sudo apt-get install vagrant

* Install git

* Install virtual box 

* run orchestrator
orchestrator.py computing_environment training_data_uri test_data_uri


e.g. python2.7 orchestrator.py 01.linux/01.centos/01.mahout/ https://raw.githubusercontent.com/crowdrec/datasets/master/01.MovieTweetings/datasets/snapshots_10K/evaluation/training/data.dat https://raw.githubusercontent.com/crowdrec/datasets/master/01.MovieTweetings/datasets/snapshots_10K/evaluation/test/data.dat /tmp/


The orchestrator:   
**    updates git repositories
**    run the orhcestrator virtual machine
**    runs the specified computing environment (using Vagrant)
**    provisions the computing environment (using Puppet):   
***        prepares the directory between the orchestrator and the computing environment   
***        installs java and maven   
***        compiles the algorithm    
***        executes the algorithm   
**    create test data
**    provides the computing environment with data (command READ_INPUT)
**    trains the algorithm (command TRAIN)   
**    requests for recommendations for some users (command RECOMMEND)   
**    terminates the the algorthm (command SHUTDOWN)   
Results will be stored in your local machine: /tmp/messaging/output_recommendations.1   


ORCHESTRATOR MESSAGES FLOW

READY (CE) -> TRAIN (O) -> OK (CE) -> START_RECOMMEND (O) -> OK (KE)


