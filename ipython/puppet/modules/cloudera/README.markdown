#Cloudera Manager

[![Build Status](https://secure.travis-ci.org/razorsedge/puppet-cloudera.png?branch=master)](http://travis-ci.org/razorsedge/puppet-cloudera)

####Table of Contents

1. [Overview](#overview)
2. [Module Description - What the module does and why it is useful](#module-description)
3. [Setup - The basics of getting started with this module](#setup)
    * [What this module affects](#what-this-module-affects)
    * [What this module requires](#requirements)
    * [Beginning with this module](#beginning-with-this-module)
    * [Upgrading](#upgrading)
4. [Usage - Configuration options and additional functionality](#usage)
    * [TLS Security](#tls-security)
    * [External Database](#external-database)
    * [Parcels](#parcels)
    * [LZO Compression](#lzo-compression)
5. [Reference - An under-the-hood peek at what the module is doing and how](#reference)
6. [Limitations - OS compatibility, etc.](#limitations)
    * [OS Support](#os-support)
    * [Software Support](#software-support)
    * [Notes](#notes)
    * [Issues](#issues)
7. [Development - Guide for contributing to the module](#development)

##Overview

This Puppet module manages the installation and configuration of [Cloudera Manager](http://www.cloudera.com/content/cloudera/en/products-and-services/cloudera-enterprise/cloudera-manager.html), a management application for Apache Hadoop, on the Cloudera official [supported operating systems](http://www.cloudera.com/content/cloudera-content/cloudera-docs/CM5/latest/Cloudera-Manager-Installation-Guide/cm5ig_cm_requirements.html?scroll=cmig_topic_4_1_unique_1).

##Module Description

This module manages the installation of [Cloudera Manager](http://www.cloudera.com/content/cloudera/en/products-and-services/cloudera-enterprise/cloudera-manager.html), a management application for Apache Hadoop.  It follows the standards written in the [Cloudera Manager Installation Guide](http://www.cloudera.com/content/cloudera-content/cloudera-docs/CM5/latest/Cloudera-Manager-Installation-Guide/Cloudera-Manager-Installation-Guide.html) "[Installation Path B - Installation Using Your Own Method](http://www.cloudera.com/content/cloudera-content/cloudera-docs/CM5/latest/Cloudera-Manager-Installation-Guide/cm5ig_install_path_B.html)".  By default, this module assumes that [parcels](http://blog.cloudera.com/blog/2013/05/faq-understanding-the-parcel-binary-distribution-format/) will be used to deploy [Cloudera's Distribution of Apache Hadoop (CDH)](http://www.cloudera.com/content/cloudera/en/products-and-services/cdh.html) and related software.  If parcels are not desired, this module can also manage the installation of CDH including HDFS & MapReduce, Impala, Sentry, Search, Spark, HBase, and [LZO compression](http://www.cloudera.com/content/cloudera-content/cloudera-docs/CM5/latest/Cloudera-Manager-Installation-Guide/cm5ig_install_lzo_compression.html).  The module can also configure [TLS security](http://www.cloudera.com/content/cloudera-content/cloudera-docs/CM5/latest/Cloudera-Manager-Administration-Guide/cm5ag_config_tls_security.html) of the Cloudera Manager communications channels, and set up Cloudera Manager to use an alternative to the [embedded database](http://www.cloudera.com/content/cloudera-content/cloudera-docs/CM5/latest/Cloudera-Manager-Installation-Guide/cm5ig_install_path_B.html?scroll=cmig_topic_6_6_5_unique_1).

[![Cloudera Certified](https://raw.githubusercontent.com/razorsedge/puppet-cloudera/master/logo_Cloudera_Certified.jpg)](http://www.cloudera.com/content/cloudera/en/partners/certified-technology.html) This module is certified on Cloudera 5.

##Setup

###What this module affects

* Installs the Cloudera software repository for CM.
* Installs Oracle Java Development Kit (JDK) 7.
* Optionally installs the Oracle Java Cryptography Extensions.
* Installs the CM agent.
* Configures the CM agent to talk to a CM server.
* Starts the CM agent.
* Sets the [kernel vm.swappiness](http://www.cloudera.com/content/cloudera/en/documentation/cdh5/v5-0-0/CDH5-Installation-Guide/cdh5ig_tips_guidelines.html) to 0.
* Disables the [kernel transparent hugepage compaction](http://www.cloudera.com/content/cloudera/en/documentation/cdh5/v5-0-0/CDH5-Installation-Guide/cdh5ig_tips_guidelines.html).
* Separately installs the CM server and database connectivity (by default to the embedded database server).
* Separately starts the CM server.
* Optionally installs the Cloudera software repository for CDH.
* Optionally installs most components of CDH 5 including HBase, Impala, Search, and Spark.
* Optionally installs GPL Extras (LZO).

###Requirements

Please read through the [Cloudera Manager Requirements](http://www.cloudera.com/content/cloudera-content/cloudera-docs/CM5/latest/Cloudera-Manager-Installation-Guide/cm5ig_cm_requirements.html) document in order to discover all of the entities (ie operating systems, databases, and browsers) supported by Cloudera Manager.  Pay close attention to the [Resource Requirements](http://www.cloudera.com/content/cloudera-content/cloudera-docs/CM5/latest/Cloudera-Manager-Installation-Guide/cm5ig_cm_requirements.html?scroll=cmig_topic_4_3_2_unique_1) and [Networking and Security Requirements](http://www.cloudera.com/content/cloudera-content/cloudera-docs/CM5/latest/Cloudera-Manager-Installation-Guide/cm5ig_cm_requirements.html?scroll=cmig_topic_4_3_3_unique_1) sections.  There are a number of requirements that this module cannot easily configure for your environment (ie No blocking by Security-Enhanced Linux (SELinux)) and which you must ensure are correct on your platform.

###Beginning with this module

Most nodes  that will be a part of a Hadoop cluster will use this declaration.
```puppet
class { '::cloudera':
  cm_server_host => 'smhost.localdomain',
}
```

The node that will be the CM server (ie smhost.localdomain) will use this declaration. This should only be included on one node of your environment.  By default it will install the embedded PostgreSQL database on the same node.  With the [correct parameters](#external-database), it can instead connect to local or remote MySQL, PostgreSQL, or Oracle RDBMS databases.
```puppet
class { '::cloudera':
  cm_server_host   => 'smhost.localdomain',
  install_cmserver => true,
}
```

###Upgrading

####Deprecation Warning

- The default for `use_parcels` will switch to `true` before the 1.0.0 release.

This:
```puppet
class { '::cloudera':
  cm_server_host => 'smhost.localdomain',
}
```
would become this:
```puppet
class { '::cloudera':
  cm_server_host => 'smhost.localdomain',
  use_parcels    => false,
}
```

- The [puppetlabs/mysql](https://forge.puppetlabs.com/puppetlabs/mysql) dependency will update to version 2 before the 1.0.0 release.  Make sure to review its changelog in the case of an upgrade.

- The class `::cloudera::repo` will be renamed to `::cloudera::cdh::repo` and the Impala repository will be split out into `::cloudera::impala::repo` before the 1.0.0 release.

This:
```puppet
class { '::cloudera::repo':
  cdh_version => '4.1',
  cm_version  => '4.1',
}
```
would become this:
```puppet
class { '::cloudera::cdh::repo':
  version => '4.1',
}
class { '::cloudera::impala::repo':
  version => '4.1',
}
```

- The class parameters and variables `yumserver` and `yumpath` have been renamed to `reposerver` and `repopath` respectively for the 2.0.0 release.  This makes the name more generic as it applies to APT and Zypprepo as well as YUM package repositories.

This:
```puppet
class { 'cloudera':
  cm_yumserver => 'http://packageserver.localdomain',
  cm_yumpath   => '/gplextras/',
}
```
would become this:
```puppet
class { 'cloudera':
  cm_reposerver => 'http://packageserver.localdomain',
  cm_repopath   => '/gplextras/',
}
```

- The `use_gplextras` parameter has been renamed to `install_lzo` for the 2.0.0 release.

This:
```puppet
class { 'cloudera':
  cm_server_host => 'smhost.example.com',
  use_gplextras  => true,
}
```
would become this:
```puppet
class { 'cloudera':
  cm_server_host => 'smhost.example.com',
  install_lzo    => true,
}
```

- The [puppetlabs/postgresql](https://forge.puppetlabs.com/puppetlabs/postgresql) dependency will update to version 3 or newer for the 3.0.0 release.  Make sure to review its changelog in the case of an upgrade.

- The [herculesteam/augeasproviders](https://forge.puppetlabs.com/herculesteam/augeasproviders) modules will replace [domcleal/augeasproviders](https://forge.puppetlabs.com/domcleal/augeasproviders) for the 3.0.0 release.


##Usage

All interaction with the cloudera module can be done through the main cloudera class.  This means you can simply toggle the options in `::cloudera` to have full functionality of the module.

###TLS Security
Level 1: [Configuring TLS Encryption only for Cloudera Manager](http://www.cloudera.com/content/cloudera-content/cloudera-docs/CM5/latest/Cloudera-Manager-Administration-Guide/cm5ag_config_tls_encr.html)

Level 2: [Configuring TLS Authentication of Server to Agents](http://www.cloudera.com/content/cloudera-content/cloudera-docs/CM5/latest/Cloudera-Manager-Administration-Guide/cm5ag_config_tls_auth.html)

Level 3: [Configuring TLS Authentication of Agents to Server](http://www.cloudera.com/content/cloudera-content/cloudera-docs/CM5/latest/Cloudera-Manager-Administration-Guide/cm5ag_config_tls_agent_auth.html)

This module's deployment of TLS provides both level 1 and level 2 configuration (encryption and authentication of the server to the agents).  Level 3 is not presently implemented.  You will need to provide a TLS certificate and the signing certificate authority for the CM server.  See the File resources in the below example for where the files need to be deployed.

There are some settings inside CM that can only be configured manually.  See the [Level 1](http://www.cloudera.com/content/cloudera-content/cloudera-docs/CM5/latest/Cloudera-Manager-Administration-Guide/cm5ag_config_tls_encr.html) instructions for the details of what to change in the WebUI and use the below values:

    Setting                       Value
    Use TLS Encryption for Agents (check)
    Path to TLS Keystore File     /etc/cloudera-scm-server/keystore
    Keystore Password             The value of server_keypw in Class['::cloudera::cm5::server'].
    Use TLS Encryption for        (check)
      Admin Console

The node that will be the CM agent may use this declaration:
```puppet
class { '::cloudera':
  server_host => 'smhost.localdomain',
  use_tls     => true,
  install_jce => true,
}
file { '/etc/pki/tls/certs/cloudera_manager.crt': }
```

The node that will be the CM agent+server may use this declaration:
```puppet
class { '::cloudera':
  server_host      => 'smhost.localdomain',
  install_cmserver => true,
  use_tls          => true,
  install_jce      => true,
  server_keypw     => 'myPassWord',
}
file { '/etc/pki/tls/certs/cloudera_manager.crt': }
file { '/etc/pki/tls/certs/cloudera_manager-ca.crt': }
file { "/etc/pki/tls/certs/${::fqdn}-cloudera_manager.crt": }
file { "/etc/pki/tls/private/${::fqdn}-cloudera_manager.key": }
```

###External Database

If you decide not to use the embedded database, the Cloudera Manager server database configuration can be completed by configuring this module to call the [`scm_prepare_database.sh`](http://www.cloudera.com/content/cloudera-content/cloudera-docs/CM5/latest/Cloudera-Manager-Installation-Guide/cm5ig_install_path_B.html?scroll=cmig_topic_6_6_5_unique_1__section_y3j_pyp_bm_unique_1) script.  The external database must be configured and ready for connection with the supplied credentials via some method outside of this module.

```puppet
class { '::cloudera':
  cm_server_host   => 'smhost.localdomain',
  install_cmserver => true,
  db_type          => 'postgresql',
  db_host          => 'dbhost.localdomain',
  db_port          => '5432',
  db_user          => 'root',
  db_pass          => 'SeCrEt',
}
```

###Parcels

[Parcel](http://blog.cloudera.com/blog/2013/05/faq-understanding-the-parcel-binary-distribution-format/) is an alternative binary distribution format supported by Cloudera Manager 4.5+ that simplifies distribution of CDH and other Cloudera products.  By default, this module assumes software deployment of CDH via parcel.  To allow Cloudera Manager to install CDH via RPMs (or DEBs) instead of parcels, just set `use_parcels => false`.

Nodes that will be cluster members will use this declaration:
```puppet
class { '::cloudera':
  cm_server_host => 'smhost.localdomain',
  use_parcels    => false,
}
```

For more advanced use cases, nodes that will be gateways may use this declaration to install extra parts of CDH:
```puppet
class { '::cloudera':
  cm_server_host => 'smhost.localdomain',
  use_parcels    => false,
}
class { '::cloudera::cdh5::mahout': }
class { '::cloudera::cdh5::kite': }
# Install Oozie WebUI support (optional):
class { '::cloudera::cdh5::oozie::ext': }
# Install MySQL support (optional):
class { '::cloudera::cdh5::hue::mysql': }
class { '::cloudera::cdh5::oozie::mysql': }
```

For more advanced use cases, the node that will be just the CM server may use this declaration:
(This will skip installation of the CDH software as it is not required.)
```puppet
class { '::cloudera::cm5::repo': } ->
class { '::cloudera::java5': } ->
class { '::cloudera::java5::jce': } ->
class { '::cloudera::cm5': } ->
class { '::cloudera::cm5::server': }
```

###LZO Compression

Hadoop-specific [LZO](http://www.oberhumer.com/opensource/lzo/) compression libraries are available in the Cloudera GPL Extras repository.  To deploy the Hadoop-specific and also the native libraries on a non-parcel system just add `install_lzo => true` to the class declaration.  Additional configuration in Cloudera Manager will be required to [activate](http://www.cloudera.com/content/cloudera-content/cloudera-docs/CM5/latest/Cloudera-Manager-Installation-Guide/cm5ig_install_lzo_compression.html) the functionality (ignore the mention of parcels in the link to the documentation).

```puppet
class { '::cloudera':
  cm_server_host => 'smhost.localdomain',
  use_parcels    => false,
  install_lzo    => true,
}
```

To deploy the native LZO compression libraries on a parcel system just add `install_lzo => true` to the class declaration.  Additional configuration in Cloudera Manager will be required to [activate](http://www.cloudera.com/content/cloudera-content/cloudera-docs/CM5/latest/Cloudera-Manager-Installation-Guide/cm5ig_install_lzo_compression.html) the functionality.

```puppet
class { '::cloudera':
  cm_server_host => 'smhost.localdomain',
  use_parcels    => true,
  install_lzo    => true,
}
```

##Reference

###Classes

####Public Classes

* cloudera: Installs and configures Cloudera Manager.  Includes most other classes.

####Private Classes

* cloudera::java5: Installs the Oracle Java Development Kit (JDK) from the Cloudera Manager repository.
* cloudera::java5::jce: Installs the Oracle Java Cryptography Extension (JCE) unlimited strength jurisdiction policy files.
* cloudera::cm5
* cloudera::cm5::repo
* cloudera::cm5::server
* cloudera::cdh5
* cloudera::cdh5::repo
* cloudera::gplextras5
* cloudera::gplextras5::repo
* cloudera::java: Installs the Oracle Java Development Kit (JDK) from the Cloudera Manager repository.
* cloudera::java::jce: Installs the Oracle Java Cryptography Extension (JCE) unlimited strength jurisdiction policy files.
* cloudera::cm
* cloudera::cm::repo
* cloudera::cm::server
* cloudera::cdh
* cloudera::cdh::repo
* cloudera::gplextras
* cloudera::gplextras::repo
* cloudera::impala
* cloudera::impala::repo
* cloudera::search
* cloudera::search::repo
* cloudera::lzo

###Parameters

The following parameters are available in the cloudera module:

####`ensure`

Ensure if present or absent.
Default: present

####`autoupgrade`

Upgrade package automatically, if there is a newer version.
Default: false

####`service_ensure`

Ensure if service is running or stopped.
Default: running

####`service_enable`

Start service at boot.
Default: true

####`cdh_reposerver`

URI of the YUM server.
Default: http://archive.cloudera.com

####`cdh_repopath`

The path to add to the $cdh_reposerver URI.
Only set this if your platform is not supported or you know what you are doing.
Default: auto-set, platform specific

####`cdh_version`

The version of Cloudera's Distribution, including Apache Hadoop to install.
Default: 5

####`cm_reposerver`

URI of the YUM server.
Default: http://archive.cloudera.com

####`cm_repopath`

The path to add to the $cm_reposerver URI.
Only set this if your platform is not supported or you know what you are doing.
Default: auto-set, platform specific

####`cm_version`

The version of Cloudera Manager to install.
Default: 5

####`cm5_repopath`

The path to add to the $cm_reposerver URI.
Only set this if your platform is not supported or you know what you are doing.
Default: auto-set, platform specific

####`ci_reposerver`

URI of the YUM server.
Default: http://archive.cloudera.com

####`ci_repopath`

The path to add to the $ci_reposerver URI.
Only set this if your platform is not supported or you know what you are doing.
Default: auto-set, platform specific

####`ci_version`

The version of Cloudera Impala to install.
Default: 1

####`cs_reposerver`

URI of the YUM server.
Default: http://archive.cloudera.com

####`cs_repopath`

The path to add to the $cs_reposerver URI.
Only set this if your platform is not supported or you know what you are doing.
Default: auto-set, platform specific

####`cs_version`

The version of Cloudera Search to install.
Default: 1

####`cg_reposerver`

URI of the YUM server.
Default: http://archive.cloudera.com

####`cg_repopath`

The path to add to the $cg_reposerver URI.
Only set this if your platform is not supported or you know what you are doing.
Default: auto-set, platform specific

####`cg_version`

The version of Cloudera Search to install.
Default: 5

####`cm_server_host`

Hostname of the Cloudera Manager server.
Default: localhost

####`cm_server_port`

Port to which the Cloudera Manager server is listening.
Default: 7182

####`use_tls`

Whether to enable TLS on the Cloudera Manager server and agent.
Default: false

####`verify_cert_file`

The file holding the public key of the Cloudera Manager server as well as the chain of signing certificate authorities. PEM format.
Default: /etc/pki/tls/certs/cloudera_manager.crt or /etc/ssl/certs/cloudera_manager.crt

####`use_parcels`

Whether to install CDH software via parcels or packages.
Default: true

####`install_lzo`

Whether to install the native LZO compression library packages.  If *use_parcels* is false, then also install the Hadoop-specific LZO compression library packages.  You must configure and deploy the GPLextras parcel repository if *use_parcels* is true.
Default: false

####`install_java`

Whether to install the Cloudera supplied Oracle Java Development Kit.  If this is set to false, then an Oracle JDK will have to be installed prior to applying this module.
Default: true

####`install_jce`

Whether to install the Oracle Java Cryptography Extension unlimited strength jurisdiction policy files.  This requires manual download of the zip file.  See files/README_JCE.md for download instructions.
Default: false

####`install_cmserver`

Whether to install the Cloudera Manager Server.  This should only be set to true on one host in your environment.
Default: false

####`database_name`

Name of the database to use for Cloudera Manager.
Default: scm

####`username`

Name of the user to use to connect to *database_name*.
Default: scm

####`password`

Password to use to connect to *database_name*.
Default: scm

####`db_host`

Host to connect to for *database_name*.
Default: localhost

####`db_port`

Port on *db_host* to connect to for *database_name*.
Default: 3306

####`db_user`

Administrative database user on *db_host*.
Default: root

####`db_pass`

Administrative database user *db_user* password.
Default:

####`db_type`

Which type of database to use for Cloudera Manager.  Valid options are embedded, mysql, oracle, or postgresql.
Default: embedded

####`server_ca_file`

The file holding the PEM public key of the Cloudera Manager server certificate authority.
Default: /etc/pki/tls/certs/cloudera_manager-ca.crt or /etc/ssl/certs/cloudera_manager-ca.crt

####`server_cert_file`

The file holding the PEM public key of the Cloudera Manager server.
Default: /etc/pki/tls/certs/${::fqdn}-cloudera_manager.crt or /etc/ssl/certs/${::fqdn}-cloudera_manager.crt

####`server_key_file`

The file holding the PEM private key of the Cloudera Manager server.
Default: /etc/pki/tls/private/${::fqdn}-cloudera_manager.key or /etc/ssl/private/${::fqdn}-cloudera_manager.key

####`server_chain_file`

The file holding the PEM public key(s) of the Cloudera Manager server intermediary certificate authority.
Default: none

####`server_keypw`

The password used to protect the keystore.
Default: none

####`proxy`

The URL to the proxy server for the YUM repositories.
Default: absent

####`proxy_username`

The username for the YUM proxy.
Default: absent

####`proxy_password`

The password for the YUM proxy.
Default: absent

####`parcel_dir`

The directory where parcels are downloaded and distributed.
Default: /opt/cloudera/parcels

##Limitations

###OS Support:

Cloudera official [supported operating systems for CM4](http://www.cloudera.com/content/cloudera/en/documentation/cloudera-manager/v4-latest/Cloudera-Manager-Installation-Guide/cmig_cm_requirements.html#cmig_topic_4_1_unique_1) and [supported operating systems for CM5](http://www.cloudera.com/content/cloudera-content/cloudera-docs/CM5/latest/Cloudera-Manager-Installation-Guide/cm5ig_cm_requirements.html?scroll=cmig_topic_4_1_unique_1).

* RedHat family - tested on CentOS 5.9, CentOS 6.4
* SuSE family   - tested on SLES 11SP3
* Debian family - tested on Debian 6.0.7, Debian 7.0, Ubuntu 10.04.4 LTS, and Ubuntu 12.04.2 LTS

###Software Support:

* Cloudera Manager    - tested with 4.1.2, 4.8.0, and 5.0.0beta2
* CDH                 - tested with 4.1.2 and 4.5.0, 5.0.0beta2
* Cloudera Impala     - tested with 1.0 and 1.2.3
* Cloudera Search     - tested with 1.1.0
* Cloudera GPL Extras - tested with 4.3.0 and 5.0.0

###Notes:

* Supports Top Scope variables (i.e. via Dashboard) and Parameterized Classes.
* Based on the [Cloudera Manager 5.0.0 Beta 2 Installation Guide](http://www.cloudera.com/content/cloudera-content/cloudera-docs/CM5/latest/PDF/Cloudera-Manager-Installation-Guide.pdf)
* TLS certificates must be in PEM format and are not deployed by this module.
* When using parcels, the CDH software is not deployed by Puppet.  Puppet will only install the Cloudera Manager server/agent.  You must then configure Cloudera Manager to deploy the parcels.
* When installing packages and not parcels on SLES, SP2 is required as the hadoop-2.0.0+1518-1.cdh4.5.0.p0.24.sles11.x86_64 package requires netcat-openbsd which is not available on SLES 11SP1.
* Osfamily RedHat 5 requires the EPEL YUM repository when installing LZO support.
* This module does not support upgrading from CDH4 to CDH5 packages, including Impala, Search, and GPL Extras.

###Issues:

* Need external module support for the Oracle Instant Client JDBC.
* When using an external PostgreSQL server that is on the same host as the CM server, PostgreSQL must be configured to accept connections with md5 password authentication.
* Osfamily RedHat 5 requires Python 2.6 from the EPEL YUM repository when installing the Hue service.

###TODO:

See [TODO.md](TODO.md) for more items.

##Development

Please see [DEVELOP.md](DEVELOP.md) for information on how to contribute.

Copyright (C) 2013 Mike Arnold <mike@razorsedge.org>

Licensed under the Apache License, Version 2.0.

[razorsedge/puppet-cloudera on GitHub](https://github.com/razorsedge/puppet-cloudera)

[razorsedge/cloudera on Puppet Forge](http://forge.puppetlabs.com/razorsedge/cloudera)

