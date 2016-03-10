RECO_ENGINE_ADDRESS=$1
if [ -z "$RECO_ENGINE_ADDRESS" ]
  then
    echo "Specify recommendation engine address: http://<host>:port."
    exit 1
fi
BASEDIR="$(cd -P "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ -n "$AWS_ACCESS_KEY_ID" ] && [ -n "$AWS_SECRET_ACCESS_KEY" ]
    then
        echo "AWS access key and secret is set, using test input file from Amazon S3."
        DATA_SOURCE="s3://idomaar-test/2014-07-01.data.idomaar_1k.txt"
    else
        echo "AWS access key or secret is not set, using test input file included in the datastream VM."
        DATA_SOURCE="newsreel-test/2014-07-01.data.idomaar_1k.txt.gz"
fi
exec $BASEDIR/../idomaar.sh --comp-env-address $RECO_ENGINE_ADDRESS --data-source $DATA_SOURCE --newsreel --new-topic