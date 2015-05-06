  
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
	}
	##  } ->

    # copy everything
##	exec { "cp 20141112__CLEF-NewsREEL-Template.zip /mnt/algo/target/":
##    cwd        => '/mnt/algo',
##    creates => "/mnt/algo/20141112__CLEF-NewsREEL-Template.tgz",
##    path => ["/usr/bin", "/usr/sbin", "/bin", "/sbin"],
##   timeout => 600
##    } ->
  
   # extract the content
##    exec { "tar xvzf /mnt/algo/20141112__CLEF-NewsREEL-Template.tgz --directory /mnt/algo/":
##    cwd        => '/mnt/algo/',
##    creates => "/mnt/algo/target",
##    path => ["/usr/bin", "/usr/sbin", "/bin", "/sbin"],
##    timeout => 900
##    } ->
   
	# Execute algorithm
##	exec { "/mnt/algo/clef-newsreel-template.sh":
##	cwd        => '/mnt/algo',
##	path => ["/usr/bin", "/usr/sbin", "/bin", "/sbin"],
##	require => Class["jdk_oracle"],
##	} 


