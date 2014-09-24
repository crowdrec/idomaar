  
    # Install base packages
    $enhancers = [ "wget", "unzip", "git" ]
    package { $enhancers: }

	 # Disable SELinux
    class { 'selinux':
        mode => 'disabled'
    }
    
    # Disable iptables
    class { 'firewall':
        ensure => 'stopped'
    }

    # Install java
    class { 'jdk_oracle':
      version => '6',
      platform => "x86",
      install_dir => '/opt/'
    } ->
    file { '/opt/java':
      ensure => 'link',
      target => '/opt/java_home'
    } ->

  # Install Maven
  class { "maven::maven":
    version => "3.2.1", # version to install
    # you can get Maven tarball from a Maven repository instead than from Apache servers, optionally with a user/password
    repo => {
      #url => "http://repo.maven.apache.org/maven2",
      #username => "",
      #password => "",
    },
    require => Class["jdk_oracle"],
    before => Exec["mvn clean compile assembly:single"]
  } ->

  # Compile algorithm
  exec { "mvn clean compile assembly:single":
    cwd        => '/mnt/algo',
    creates => "/mnt/algo/target/crowdrec-mahout-test-1.0-SNAPSHOT-jar-with-dependencies.jar",
    path => ["/usr/bin", "/usr/sbin", "/bin", "/sbin"],
    timeout => 600
  } ->

  # Create startup script for algorithm
  exec { "cp itembasedrec.sh /etc/init.d/itembasedrec":
    cwd        => '/mnt/algo',
    creates => "/etc/init.d/itembasedrec",
    path => ["/usr/bin", "/usr/sbin", "/bin", "/sbin"],
    timeout => 5
  } ->  

  # Enable algo startup at boot
  service { "itembasedrec":
    enable => true,
  }

  # Execute algorithm
  exec { "/mnt/algo/itembasedrec.sh start":
    cwd        => '/mnt/algo',
    path => ["/usr/bin", "/usr/sbin", "/bin", "/sbin"],
    require => Exec["mvn clean compile assembly:single"]
  } 

