#!/bin/sh
# $1 = ALGO directory, relative to base algo dir
# $2 = COMPUTE env directory, relative to base compute envs dir
# $3 = DATA directory, relative to base data dir

# EG orchestrator.sh 01.java/01.mahout/01.example/ 01.linux/01.centos/01.mahout/ 01.MovieTweetings/datasets/snapshots_10K/

BASEDIR=/home/davide/sources/crowdrec/reference-framework
STAGEDIR=$1
BASEMSG_IN=cmd_in.msg
INF=$BASEDIR/$BASEMSG_IN
OUTF=$BASEDIR/cmd_out.msg

ALGO_DIR=$BASEDIR/../algorithms
DATA_DIR=$BASEDIR/../datasets
COMPUTING_ENV_DIR=$BASEDIR/../computingenvironments
MESSAGING_DIR=$BASEDIR/.messaging

SDIR=./resources/

FNAME=$BASEDIR/output_filename.1

echo "cleaning"
rm -f $FNAME
rm -f $INF
rm -f $OUTF
if [ -f .pid ]; then
	kill -9 `cat .pid`
fi
mkdir -p $MESSAGING_DIR
mkdir -o $MESSAGING_DIR/msg
mkdir -o $MESSAGING_DIR/data


echo "DO: Update git REPOs"
cd $ALGO_DIR
git pull

cd $DATA_DIR
git pull

cd $COMPUTING_ENV_DIR
git pull

# TODO: creating train/test sets

# TODO: separate libraries from core algorithm
echo "DO: starting machine"
cd $COMPUTING_ENV_DIR/$2
SHARED_ALGO=$ALGO_DIR/$1 SHARED_DATA=$DATA_DIR/$3 SHARED_MSG=$MESSAGGING_DIR vagrant up 

echo "STATUS: waiting for machine to be ready"
while [ ! -f $OUTF ] ; 
do
        sleep 2
done
if [ `cat $OUTF` = "READY" ]; then
	echo "INFO: machine started"
else
	echo "WARN: machine failed to start. Process stopped."
	exit
fi
rm -f $OUTF

echo "DO: read input"
cp $SDIR/$BASEMSG_IN.read $INF
while [ ! -f $OUTF ] ; 
do
	sleep 2
done
if [ `cat $OUTF` = "OK" ]; then
        echo "INFO: input correctly read"
else
        echo "WARN: some errors while processing input. Process stopped."
        exit
fi
rm -f $OUTF

echo "DO: train"  
cp $SDIR/$BASEMSG_IN.train $INF
while [ ! -f $OUTF ] ; 
do 
        sleep 2
done
if [ `cat $OUTF` = "OK" ]; then
        echo "INFO: recommender correctly trained"
else
        echo "WARN: some errors while training the recommender. Process stopped."
        exit
fi
rm -f $OUTF

echo "DO: recommend"
cp $SDIR/$BASEMSG_IN.recommend $INF
while [ ! -f $OUTF ] ; 
do 
        sleep 2
done
if [ `cat $OUTF` = "OK" ]; then
        echo "INFO: recommendations correctly generated"
else
        echo "WARN: some errors while generating recommendations. Process stopped."
        exit
fi
rm -f $OUTF

echo "DO: stop"
cp $SDIR/$BASEMSG_IN.stop $INF

echo ""
echo ""
echo "== recommendations == "
cat $FNAME

# TODO: test/evaluate the output
sleep 5
kill -9 $pid
rm -f .pid
echo "INFO: finished"
