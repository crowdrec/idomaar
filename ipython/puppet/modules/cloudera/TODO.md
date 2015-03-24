# TODO
## For 1.0.0 release:

* default parcels
* update dependencies (mysql/postgresql)
* separate install impala (manifests/impala/bla.pp)
* separate install search (manifests/search/bla.pp)
* support SLES/Debian/Ubuntu
* clean out commented code

## For 2.0.0 release:

* support CM5 / CDH5 / Oracle JDK 7
* integrate cloudera::cm::server into init.pp
* Set [kernel vm.swappiness](http://www.cloudera.com/content/cloudera-content/cloudera-docs/CDH5/latest/CDH5-Installation-Guide/cdh5ig_topic_11_6.html) to 0.
* Do parcels still require LZO OS libraries?

## Other:

* refactor ::repo to autoinclude in cdh/impala/search
* Support TLS level 3.
* PostgreSQL must be configured to accept connections with md5 password authentication.  To do so, edit /var/lib/pgsql/data/pg_hba.conf (or similar) to include `host all all 127.0.0.1/32 md5` *above* a similar line that allows `ident` authentication.
* cm_api support.
* Add HDFS FUSE mounting support.
* Support pig-udf installation.
* Document hive-server installation.
* Document hive-metastore installation.
* Document sqoop-metastore installation.
* Document whirr installation.
* Sqoop: [Installing the JDBC Drivers](http://www.cloudera.com/content/cloudera-content/cloudera-docs/CDH5/latest/CDH5-Installation-Guide/cdh5ig_topic_13_7.html)
* Hue: [EL5 requires python26 from EPEL](http://www.cloudera.com/content/cloudera-content/cloudera-docs/CM5/latest/Cloudera-Manager-Installation-Guide/cm5ig_install_path_A.html)

## Links

http://www.cloudera.com/content/cloudera-content/cloudera-docs/CM5/latest/Cloudera-Manager-Version-and-Download-Information/Cloudera-Manager-Version-and-Download-Information.html
http://archive.cloudera.com/cm5/redhat/6/x86_64/cm/5/

http://www.cloudera.com/content/cloudera-content/cloudera-docs/CDH5/latest/CDH-Version-and-Packaging-Information/cdhvd_topic_2.html
http://archive.cloudera.com/cdh5/redhat/6/x86_64/cdh/5/

http://www.cloudera.com/content/cloudera-content/cloudera-docs/Search/latest/Cloudera-Search-Version-and-Download-Information/Cloudera-Search-Version-and-Download-Information.html
http://archive.cloudera.com/search/redhat/6/x86_64/search/

http://www.cloudera.com/content/cloudera-content/cloudera-docs/Impala/latest/Cloudera-Impala-Version-and-Download-Information/Cloudera-Impala-Version-and-Download-Information.html
http://archive.cloudera.com/impala/redhat/6/x86_64/impala/

http://www.cloudera.com/content/cloudera-content/cloudera-docs/CM4Ent/latest/Cloudera-Manager-Installation-Guide/cmig_install_LZO_Compression.html
http://archive.cloudera.com/gplextras5/redhat/6/x86_64/gplextras/
http://archive.cloudera.com/gplextras/redhat/6/x86_64/gplextras/

