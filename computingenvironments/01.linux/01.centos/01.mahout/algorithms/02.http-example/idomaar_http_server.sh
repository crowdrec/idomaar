#!/bin/bash
# chkconfig: 2345 95 20
# description: Idomaar HTTP server
#
# processname: idomaar_http_server

THIS_HOST_IP=192.168.22.100
LOG=/vagrant/algorithms/02.http-example/idomaar_http_server.log
echo "idomaar_http_server service" $1 >> $LOG

case $1 in
    status)
        status=`ps aux | grep idomaar_http_server | grep python | wc -l`
        echo status $status >> $LOG
        $0 start
        #exit 0
    ;;
    start)
	    echo "starting idomaar_http_server service"
        cd /vagrant/algorithms/02.http-example
        ORCH=`netstat -rn | grep "^0.0.0.0 " | cut -d " " -f10`
        echo executing nohup python3 /vagrant/algorithms/02.http-example/idomaar_http_server.py >> $LOG
        #Sleep 1 at the end to work around vagrant ssh nohup issue (nohup processes are stl shut down on exit)
        nohup python3 idomaar_http_server.py >> $LOG & sleep 1
        echo "Started." >> $LOG
    ;;
    stop)
	   echo "stopping idomaar_http_server service" >> $LOG
	   	pid=`ps aux | grep idomaar_http_server | grep python | awk '{print $2}'`
        kill -9 $pid
    ;;
esac
exit 0
