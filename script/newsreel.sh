if [ $# -ne 2 ] 
    then 
    	echo "usage: newsreel.sh <recommendation-engine-address> <data-source>"
    	echo "e.g. newsreel.sh http://host:port /path/to/data/file"
    	exit 1
fi
RECO_ENGINE_ADDRESS=$1
DATA_SOURCE=$2
BASEDIR="$(cd -P "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec $BASEDIR/../idomaar.sh --comp-env-address $RECO_ENGINE_ADDRESS --data-source $DATA_SOURCE --newsreel --new-topic