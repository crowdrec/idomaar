# Java Cryptography Extension
Go to Oracle's [Java download page](http://www.oracle.com/technetwork/java/javase/downloads/index.html) and download the Java Cryptography Extension (JCE) unlimited strength jurisdiction policy files zipfile to this directory.

## JCE 6

    cd /etc/puppet/modules/cloudera/files
    wget -c --no-cookies --no-check-certificate --header "Cookie: gpw_e24=http%3A%2F%2Fwww.oracle.com" \
      http://download.oracle.com/otn-pub/java/jce_policy/6/jce_policy-6.zip -O jce_policy-6.zip
    unzip jce_policy-6.zip

You should have the following structure:

    $ tree files/
    files/
    |-- java.sh
    |-- jce
    |   |-- COPYRIGHT.html
    |   |-- local_policy.jar
    |   |-- README.txt
    |   `-- US_export_policy.jar
    |-- jce_policy-6.zip
    `-- README_JCE.md
    
    1 directory, 7 files


## JCE 7

    cd /etc/puppet/modules/cloudera/files
    wget -c --no-cookies --no-check-certificate --header "Cookie: gpw_e24=http%3A%2F%2Fwww.oracle.com" \
      http://download.oracle.com/otn-pub/java/jce/7/UnlimitedJCEPolicyJDK7.zip -O jce_policy-7.zip
    unzip jce_policy-7.zip

You should have the following structure:

    $ tree files/
    files/
    |-- java.sh
    |-- jce_policy-7.zip
    |-- README_JCE.md
    `-- UnlimitedJCEPolicy
        |-- local_policy.jar
        |-- README.txt
        `-- US_export_policy.jar
    
    1 directory, 6 files

