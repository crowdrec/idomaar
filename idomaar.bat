vagrant -v
set basedir=%~dp0
cd %basedir%/datastreammanager
echo Working directory is %cd%
echo Bringing up datastream manager VM via vagrant ...
vagrant up
set orchestrator_command=sudo python /vagrant/orchestrator/main/orchestrator_cli.py
set orchestrator_args=%*
echo Arguments received %orchestrator_args%
echo Executing %orchestrator_command% %orchestrator_args% on datastreammanager vm ...
vagrant ssh -c "%orchestrator_command% %orchestrator_args%"