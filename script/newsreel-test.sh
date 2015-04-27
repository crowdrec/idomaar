RECO_ENGINE_ADDRESS=$1
if [ -z "$RECO_ENGINE_ADDRESS" ]
  then
    echo "Specify recommendation engine address: http://<host>:port."
    exit 1
fi
BASEDIR="$(cd -P "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec $BASEDIR/../idomaar.sh --comp-env-address $RECO_ENGINE_ADDRESS --data-source /vagrant/data/newsreel-test/2014-07-01.data.idomaar_1k.txt --newsreel --new-topic