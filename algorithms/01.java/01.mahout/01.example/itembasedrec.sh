#!/bin/bash
# chkconfig: 2345 95 20
# description: Mahout recommendation algo example
#
# processname: itembasedrec

LOG=/tmp/mahout.log
echo "itembasedrec service" $1 >> $LOG

case $1 in
    status)
        status=`ps aux | grep dev.crowdrec.recs.mahout.ItembasedRec_batch | grep java | wc -l`
        echo status $status >> $LOG
        $0 start
        #exit 0
    ;;
    start)
	    echo "starting itembasedrec service" >> $LOG
        sleep 30
        cd /mnt/algo
        ORCH=`netstat -rn | grep "^0.0.0.0 " | cut -d " " -f10`
        echo executing java -cp /mnt/algo/target/crowdrec-mahout-test-1.0-SNAPSHOT-jar-with-dependencies.jar dev.crowdrec.recs.mahout.ItembasedRec_batch /tmp tcp://$ORCH:2760 >> $LOG
        java -cp /mnt/algo/target/crowdrec-mahout-test-1.0-SNAPSHOT-jar-with-dependencies.jar dev.crowdrec.recs.mahout.ItembasedRec_batch /tmp tcp://$ORCH:2760 >> $LOG &
    ;;
    stop)
	   echo "stopping itembasedrec service" >> $LOG
        pid=`ps aux | grep dev.crowdrec.recs.mahout.ItembasedRec_batch | grep java |awk '{print $2}'`
        kill -9 $pid
    ;;
esac
exit 0
