# SELinux Puppet Module

[![Build Status](https://travis-ci.org/spiette/puppet-selinux.png?branch=master)](https://travis-ci.org/spiette/puppet-selinux)

This module can set SELinux and compile SELinux type enforcement files (.te)
into modules deploying them to running RHEL based system. It allows you to keep
.te files in text form in a repository, while allowing the system to compile
and manage SELinux modules.

This module features:
- all enforcing/permissive/disabled switch covered
- ability to select selinux module directory
- a file context file (.fc) can be used with a type enforcement (.te) one
- error detection: it will not silently fails to compile or load a module
- once loaded, it will not create a new catalog for each run
- it will only try to load a module if loaded and source version are different.
- module enable/disable (stay loaded)
- cleanup if you remove your module
- puppet lint compliant code
- full spec testing

SELinux boolean are not part of this module as there's a resource type
(selboolean) that puppet provides. This module use the other SELinux resource
type, selmodule to load the module.

# Requirements
- puppet >= 2.7
- RedHat/Fedora based distribution

# Installation
<pre>
puppet module install spiette/selinux
</pre>

# Synopsys
## selinux class
<pre>
include selinux
</pre>

<pre>
class { 'selinux':
  mode => 'permissive'
}
</pre>
### Parameters:

- *mode*

   (enforcing|permissive|disabled)
   sets the operating state for SELinux.

- *installmake*

   make is required to install modules. If you have the make package declared
   elsewhere, you want to set this to false. It defaults to true.

## selinux::module
<pre>
selinux::module { 'rsynclocal':
  source   => 'puppet:///modules/site/rsynclocal'
}
</pre>

This will place the .te (and .fc if present) file(s) on the target machine, compile into a .pp and load the module.
`source` will be set to `puppet:///modules/selinux/${name}` by default.

<pre>
selinux::module { 'rsynclocal':
  ensure => 'disabled'
}
</pre>
This keep the module installed but disabled. You can also disable system modules.

<pre>
selinux::module { 'rsynclocal':
  ensure => 'enabled'
}
</pre>
Note: `ensure` => `present` include `ensure` => `enabled`

<pre>
selinux::module { 'rsynclocal':
  ensure => 'absent'
}
</pre>
This will remove all files related to rsynclocal on the target system.

### Parameters

- *ensure*

   (present|enabled|disabled|absent) - set the state for a module

- *modules_dir*

    The directory where modules (source files, .mod and .pp) will live on a
    system. Defaults to $vardir/selinux, can be changed in $selinux::params.

- *source*

   Source directory (either a puppet URI or local file) of the SELinux .te
   module. Defaults to `puppet:///modules/selinux/${name}`

- *ignore*

   If you want to exclude files of your selinux module to be transferred to
   the node (.svn directories for example), you can add a string to exclude
   or a list of pattern, eg. [ 'CVS', '.svn' ]. Defaults to nothing: all files
   will be copied. You can use resource defaults if you always want to ignore
   the same pattern:

    <pre>
    Selinux::Module {
      ignore => [ 'CVS', '.svn' ]
    }
    </pre>

# SELinux reference

* *selinux(8)*
* *man -k selinux* for module specific documentation
* *audit2allow(1)* to build your modules with audit log on permissive mode
* *selboolean*, *selmodule* resources type from puppet
* *selrange*, *selrole*, *seltype*, *seluser* parameters for the file resource type

# Performance impact

Many SELinux commands are slow to execute, especially on changes. Your puppet run could last a couple of minutes if you add a dozen of modules in one shot. If you're using modules, each time `semdule -l` will run (2 seconds easily), just to look if your module is loaded.

# Contribute

Please see the [Github](https://github.com/spiette/puppet-selinux) page. We'll review  pull requests and bug reports. If the module don't do what you want, please explain your use case. Please submit your pull requests in the pullrequest branch and make sure tests are running.

# Credits
- Maintainer: Simon Piette <piette.simon@gmail.com>
- Original module from James Fryman <james@frymanet.com> https://github.com/jfryman/puppet-selinux
- Concepts incorporated from:
http://stuckinadoloop.wordpress.com/2011/06/15/puppet-managed-deployment-of-selinux-modules/
