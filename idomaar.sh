#!/bin/bash
vagrant -v
BASEDIR="$(cd -P "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd $BASEDIR/datastreammanager
echo "Working directory is" `pwd`
echo "Bringing up datastream manager VM via vagrant ..."
vagrant up
ORCHESTRATOR_COMMAND="sudo python /vagrant/orchestrator/main/orchestrator_cli.py"
ORCHESTRATOR_ARGS=$@
echo "Arguments received $ORCHESTRATOR_ARGS"
echo "Executing $ORCHESTRATOR_COMMAND $ORCHESTRATOR_ARGS on datastreammanager vm ..."
vagrant ssh -c ''"$ORCHESTRATOR_COMMAND $ORCHESTRATOR_ARGS"''
