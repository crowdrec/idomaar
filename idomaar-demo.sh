#!/bin/bash
vagrant -v
BASEDIR="$(cd -P "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEMO_COMPUTING_ENV=01.linux/01.centos/01.mahout
cd $BASEDIR/computingenvironments/$DEMO_COMPUTING_ENV
echo "Working directory is" `pwd`
echo "Bringing up demo computing environment $DEMO_COMPUTING_ENV"
vagrant up
echo "Starting recommender engine ..."
vagrant ssh -c 'sudo /vagrant/algorithms/01.example/itembasedrec.sh start'
cd $BASEDIR
echo "Working directory is" `pwd`
echo "Launching idomaar ..."
if [ -n "$AWS_ACCESS_KEY_ID" ] && [ -n "$AWS_SECRET_ACCESS_KEY" ]
    then
        echo "AWS access key and secret is set, using test input file from Amazon S3."
        TRAINING_URI=s3://idomaar-test/demo/training-data.dat
        TEST_URI=s3://idomaar-test/demo/test-data.dat
    else
        echo "AWS access key or secret is not set, using demo training and test data from Idomaar GitHub."
        TRAINING_URI=https://raw.githubusercontent.com/crowdrec/datasets/master/01.MovieTweetings/datasets/snapshots_10K/evaluation/training/data.dat
        TEST_URI=https://raw.githubusercontent.com/crowdrec/datasets/master/01.MovieTweetings/datasets/snapshots_10K/evaluation/test/data.dat
fi
exec ./idomaar.sh --new-topic --comp-env-address tcp://192.168.22.100:2760 --training-uri ${TRAINING_URI} --test-uri ${TEST_URI} $@
