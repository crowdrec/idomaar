#!/bin/bash
vagrant -v
BASEDIR="$(cd -P "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd $BASEDIR/datastreammanager
echo "Working directory is" `pwd`
echo "Bringing up datastream manager VM via vagrant ..."
vagrant up
ORCHESTRATOR_ENVIRONMENT="AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY"
ORCHESTRATOR_COMMAND="sudo $ORCHESTRATOR_ENVIRONMENT python /vagrant/orchestrator/main/orchestrator_cli.py"
ORCHESTRATOR_ARGS=$@
echo "Arguments received $ORCHESTRATOR_ARGS"
echo "Executing $ORCHESTRATOR_COMMAND $ORCHESTRATOR_ARGS on datastreammanager vm ..."
vagrant ssh -c ''"$ORCHESTRATOR_ENVIRONMENT $ORCHESTRATOR_COMMAND $ORCHESTRATOR_ARGS"''
