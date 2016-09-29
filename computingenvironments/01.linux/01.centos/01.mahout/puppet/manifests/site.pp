  
   # Install base packages
    $enhancers = [ "wget", "unzip", "git" ]
    package { $enhancers: }


  # INSTALL JAVA
  include apt
  apt::ppa { "ppa:webupd8team/java": }

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
  
  # Install Maven
  class { "maven::maven":
    version => "3.2.1", # version to install
    # you can get Maven tarball from a Maven repository instead than from Apache servers, optionally with a user/password
    repo => {
      #url => "http://repo.maven.apache.org/maven2",
      #username => "",
      #password => "",
    },
    require => Package["oracle-java7-installer"],
    before => Exec["mvn clean compile assembly:single"]
  } ->

  # Compile algorithm
  exec { "mvn clean compile assembly:single":
    cwd        => '/vagrant/algorithms/01.example/',
    creates => "/vagrant/algorithms/01.example/target/crowdrec-mahout-test-1.0-SNAPSHOT-jar-with-dependencies.jar",
    path => ["/usr/bin", "/usr/sbin", "/bin", "/sbin"],
    timeout => 600
  } ->

  # Create startup script for algorithm
  exec { "cp idomaar_http_server.sh /etc/init.d/idomaar_http_server":
    cwd        => '/vagrant/algorithms/02.http/',
    # creates => "/etc/script/idomaar_http_server",
    path => ["/usr/bin", "/usr/sbin", "/bin", "/sbin"],
    timeout => 60
  } ->  

  # Enable algo startup at boot
  service { "gru":
    enable => true,
    ensure => running
  }


