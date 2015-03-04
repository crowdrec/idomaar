#!/bin/bash
# chkconfig: 2345 95 20
# description: Mahout recommendation algo example
#
# processname: itembasedrec

LOG=/tmp/mahout.log
echo "itembasedrec service" $1 >> $LOG

case $1 in
    status)
        status=`ps aux | grep eu.crowdrec.recs.mahout.ItembasedRec_batch | grep java | wc -l`
        echo status $status >> $LOG
        $0 start
        #exit 0
    ;;
    start)
	    echo "starting itembasedrec service" >> $LOG
        cd /vagrant/algorithms/01.example
        ORCH=`netstat -rn | grep "^0.0.0.0 " | cut -d " " -f10`
        echo executing java -cp /vagrant/algorithms/01.example/target/crowdrec-mahout-test-1.0-SNAPSHOT-jar-with-dependencies.jar eu.crowdrec.recs.mahout.ItembasedRec_batch /tmp tcp://0.0.0.0:2760 >> $LOG
        #java -cp /vagrant/algorithms/01.example/target/crowdrec-mahout-test-1.0-SNAPSHOT-jar-with-dependencies.jar eu.crowdrec.recs.mahout.ItembasedRec_batch /tmp "tcp://*:2760" >> $LOG &
        java -cp /vagrant/algorithms/01.example/target/crowdrec-mahout-test-1.0-SNAPSHOT-jar-with-dependencies.jar eu.crowdrec.recs.mahout.ItembasedRec_batch /tmp tcp://0.0.0.0:2760
    ;;
    stop)
	   echo "stopping itembasedrec service" >> $LOG
        pid=`ps aux | grep eu.crowdrec.recs.mahout.ItembasedRec_batch | grep java |awk '{print $2}'`
        kill -9 $pid
    ;;
esac
exit 0
