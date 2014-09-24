	include apt

	#, "mono-xbuild", "mono-gmcs"

    # Install base packages
    $enhancers = [ "unzip", "git",  "libfile-slurp-perl" ]
    package { $enhancers: }

	apt::ppa { 'ppa:directhex/monoxide': 
	} ->
	package { ["monodevelop", "mono-gmcs", "mono-xbuild"]:
    	ensure => "installed"
	} ->

  	#checkout wraprec from repo
	git::repo{'wraprec':
 		path   => '/opt/wraprec',
 		source => 'https://github.com/babakx/WrapRec'
	} ->

	# build wraprec
	exec { "xbuild WrapRec.sln":
    	cwd        => '/opt/wraprec',
    	creates => "",
    	path => ["/usr/bin", "/usr/sbin", "/bin", "/sbin"],
    	timeout => 600
  	} 

	# Download mymedialite (MyMediaLite is already included in WrapRec 
  	#exec { "wget http://mymedialite.net/download/MyMediaLite-3.10.tar.gz":
    	#cwd        => '/opt/',
    	#creates => "/opt/MyMediaLite-3.10.tar.gz",
    	#path => ["/usr/bin", "/usr/sbin", "/bin", "/sbin"],
    	#timeout => 600
  	#} ->

    
    #untar Archive
   	#exec { "tar xvfz MyMediaLite-3.10.tar.gz":
    	#cwd        => '/opt/',
    	#creates => "/opt/MyMediaLite-3.10/bin",
    	#path => ["/usr/bin", "/usr/sbin", "/bin", "/sbin"],
    	#timeout => 600
  	#} 



  	
