###
### File managed by Puppet
###
if [ -d /usr/java/default ]; then
  export JAVA_HOME=/usr/java/default
elif [ -d /usr/lib/jvm/j2sdk1.6-oracle ]; then
  export JAVA_HOME=/usr/lib/jvm/j2sdk1.6-oracle
  export PATH=${PATH}:${JAVA_HOME}/bin
elif [ -d /usr/lib/jvm/java-7-oracle-cloudera ]; then
  export JAVA_HOME=/usr/lib/jvm/java-7-oracle-cloudera
  export PATH=${PATH}:${JAVA_HOME}/bin
fi
