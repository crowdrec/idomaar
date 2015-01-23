  
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

  # Compile algorithm
  #exec { "mvn clean compile assembly:single":
  #  cwd        => '/mnt/algo',
  #  creates => "/mnt/algo/target/crowdrec-mahout-test-1.0-SNAPSHOT-jar-with-dependencies.jar",
  #  path => ["/usr/bin", "/usr/sbin", "/bin", "/sbin"],
  #  timeout => 600
  #} ->
  exec { "cp target/streamrecommender-with-dependencies.jar /mnt/algo/target/":
    cwd        => '/mnt/algo',
    creates => "/mnt/algo/target/streamrecommender-with-dependencies.jar",
    path => ["/usr/bin", "/usr/sbin", "/bin", "/sbin"],
    timeout => 600
  } ->
  
  # Create startup script for algorithm
#  exec { "cp newsstreamrec.sh /etc/script/newsstreamrec":
#    cwd        => '/mnt/algo',
#    creates => "/etc/script/newsstreamrec",
#    path => ["/usr/bin", "/usr/sbin", "/bin", "/sbin"],
#    timeout => 5
#  } ->  

  # Enable algo startup at boot
  #service { "newsstreamrec":
  #  enable => true,
  #}

  # Execute algorithm
  exec { "/mnt/algo/newsstreamrec.sh start":
    cwd        => '/mnt/algo',
    path => ["/usr/bin", "/usr/sbin", "/bin", "/sbin"],
  } 

