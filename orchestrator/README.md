* Tested with Python 2.8
* Install (pip) pyzmq and enum34

* (Install ruby if required)

* Install vagrant
e.g., on debian-based env: sudo apt-get install vagrant

* Install git

* Install virtual box 

* run orchestrator
orchestrator.py computing_env dataset_base_uri


e.g. python2.7 orchestrator.py 01.linux/01.centos/01.mahout/ https://github.com/crowdrec/datasets/tree/master/01.MovieTweetings/datasets/snapshots_10K

The orchestrator:   
**    updates git repositories
**    run the data stream manager virtual machine
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


TODO:
- autostart di mahout
