#!/bin/bash
# chkconfig: 2345 95 20
# description: Mahout recommendation algo example
#
# processname: gru

THIS_HOST_IP=192.168.22.100
LOG=/vagrant/algorithms/03.gru/gru.log
echo "gru service" $1 >> $LOG

case $1 in
    status)
        status=`ps aux | grep http_flask_server | grep python | wc -l`
        echo status $status >> $LOG
        $0 start
        #exit 0
    ;;
    start)
	    echo "starting gru service"
        cd /vagrant/algorithms/03.gru
        ORCH=`netstat -rn | grep "^0.0.0.0 " | cut -d " " -f10`
        echo executing nohup python3 /vagrant/algorithms/03.gru/http_flask_server.py >> $LOG
        #Sleep 1 at the end to work around vagrant ssh nohup issue (nohup processes are stl shut down on exit)
        nohup python3 http_flask_server.py >> $LOG & sleep 1
        echo "Started." >> $LOG
    ;;
    stop)
	   echo "stopping gru service" >> $LOG
	   	pid=`ps aux | grep http_flask_server | grep python | awk '{print $2}'`
        kill -9 $pid
    ;;
esac
exit 0
