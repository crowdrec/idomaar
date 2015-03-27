

 # INSTALL JAVA

  exec { 'apt-get update':
    command => '/usr/bin/apt-get update',
    require => Apt::Ppa["ppa:webupd8team/java"],
  } -> 
  exec {
    'set-licence-selected':
      command => '/bin/echo debconf shared/accepted-oracle-license-v1-1 select true | /usr/bin/debconf-set-selections';

    'set-licence-seen':
      command => '/bin/echo debconf shared/accepted-oracle-license-v1-1 seen true | /usr/bin/debconf-set-selections';
  } ->

  package { 'oracle-java7-installer':
    ensure => installed
  }

class { 'apt':
  always_apt_update    => false,
  apt_update_frequency => undef,
  disable_keys         => undef
}

apt::ppa { "ppa:webupd8team/java": }

exec { "import_CDH_key": 
  command => 'apt-key adv --recv-key --keyserver keyserver.ubuntu.com 327574EE02A818DD',
  user => "root",
  path => "/bin:/usr/sbin:/usr/bin"

}

apt::source { 'cdh_5':
  location          => 'http://archive.cloudera.com/cdh5/ubuntu/trusty/amd64/cdh/',
  release           => 'trusty-cdh5',
  repos             => 'contrib',
  trusted_source  	=> true,
  require => Exec['import_CDH_key']
}

# install spark, ipython and its requirements
$ipython = [ "spark", "spark-master", "spark-worker", "ipython-notebook", "spark-python", "python-pip", "python-dev", "python-numpy" ]

package { 
	$ipython: 
	ensure => "installed",
	require =>  Apt::Source['cdh_5']
 }

## fix cloudera depenency bug
exec {
    'fix_cloudera_installation_bug':
     command => '/vagrant/scripts/fix_cloudera_installation.sh',
     require => [Package[$ipython]],
     path => "/bin:/usr/sbin:/usr/bin",
     user => "root",
     creates => "/usr/lib/zookeeper/lib/slf4j-log4j12.jar"
  }


user { "ipython":
    home => "/home/ipython",
    ensure     => "present",
    managehome => true
}

exec {
    'configure_ipython':
     command => '/vagrant/scripts/install_ipython.sh',
     creates => "/home/ipython/start-ipython.sh",
     require => [Package[$ipython], User["ipython"] ],
     path => "/bin:/usr/sbin:/usr/bin",
     user => "ipython",
     environment => [ "HOME=/home/ipython" ] 
  }

exec {
    'disable_spark_logging':
     command => 'cp /vagrant/scripts/log4j.properties /etc/spark/conf',
     creates => "/etc/spark/conf/log4j.properties",
     require =>  Exec['configure_ipython'],
     path => "/bin:/usr/sbin:/usr/bin",
     user => "root"
  }