@echo off
vagrant -v
set basedir=%~dp0
echo Basedir %basedir%
set demo_computing_env=01.linux\01.centos\01.mahout
set computing_environment_dir=%basedir%computingenvironments\%demo_computing_env%
echo Computing environment directory %computing_environment_dir%
cd %computing_environment_dir%
echo Working directory is %cd%
echo Bringing up demo computing environment %demo_computing_env%
vagrant up
echo Starting recommender engine ...
vagrant ssh -c 'sudo /vagrant/algorithms/02.http-example/idomaar_http_server.sh start'
cd %basedir%
echo Working directory is %cd%
echo Launching Idomaar HTTP REST server ...
%basedir%/idomaar.bat --comp-env-address http://192.168.22.100:5000 --training-uri https://raw.githubusercontent.com/crowdrec/datasets/master/01.MovieTweetings/datasets/snapshots_10K/evaluation/training/data.dat --test-uri https://raw.githubusercontent.com/crowdrec/datasets/master/01.MovieTweetings/datasets/snapshots_10K/evaluation/test/data.dat %*