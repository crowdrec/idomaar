# == Define: selinux::module
#
#  This define will either install or uninstall a SELinux module from a running
#  system. This module allows an admin to keep .te files in text form in a
#  repository, while allowing the system to compile and manage SELinux modules.
#
# === Parameters
#
#   [*ensure*]
#     (present|absent) - sets the state for a module
#
#   [*modules_dir*]
#      The directory where compiled modules will live on a system. Defaults to
#      /usr/share/selinux declared in $selinux::params
#
#   [*source*]
#     Source directory (either a puppet URI or local file) of the SELinux .te
#     module. Defaults to puppet:///modules/selinux/${name}
#
#   [*ignore*]
#     If you want to exclude files of your selinux module to be transferred to
#     the node (.svn directories for example), you can add a string to exclude
#     or a list of pattern, eg. [ 'CVS', '.svn' ]. Defaults to nothing: all files
#     will be copied.
#
# ===  Example
#
#    selinux::module { 'rsynclocal':
#      source => 'puppet:///modules/selinux/rsynclocal',
#    }
#
define selinux::module(
  $ensure  = 'present',
  $source = undef,
  $modules_dir = undef,
  $ignore = undef,
) {
  include selinux
  include selinux::install

  $ensures = [ 'present', 'enabled', 'disabled', 'absent' ]
  if !( $ensure in $ensures ) {
    $ensure_string = join($ensures, ', ')
    fail("Selinux::Module[${name}]:
      ensure parameter should be one of ${ensure_string}")
  }

  if $modules_dir {
    $selinux_modules_dir = $modules_dir
  } else {
    $selinux_modules_dir = $selinux::params::modules_dir
  }
  # .te and .fc files will be placed on a $name directory
  $this_module_dir = "${selinux_modules_dir}/${name}"

  if $source {
    $sourcedir = $source
  } else {
    $sourcedir = "puppet:///modules/selinux/${name}"
  }
  # sourcedir validation
  # we only accept puppet:///modules/<something>/<something>, file:///anything
  # we reject .te
  case $sourcedir {
    /^puppet:\/\/\/modules\/.*.te$/: {
      fail('Invalid source parameter, expecting a directory')
    }
    /^puppet:\/\/\/modules\/[^\/]+\/[^\/]+\/?$/: { }
    /^file:\/\/\/.*$/: { }
    default: {
      fail('Invalid source parameter')
    }
  }
  if $sourcedir !~ /^((puppet|file):.*\/([^\/]*))/ {
    fail('Invalid source parameter')
  }

  # Set Resource Defaults
  File {
    owner => 'root',
    group => 'root',
    mode  => '0640',
  }

  # Only allow refresh in the event that the initial source files are updated.
  Exec {
    path        => '/sbin:/usr/sbin:/bin:/usr/bin',
    cwd         => $this_module_dir,
  }

  $active_modules = '/etc/selinux/targeted/modules/active/modules'
  $active_pp = "${active_modules}/${name}.pp"
  $compiled_pp = "${this_module_dir}/${name}.pp"
  case $ensure {
    present: {
      File[$this_module_dir]->
      File["${this_module_dir}/${name}.te"]~>
      Exec["${name}-makemod"]~>
      Selmodule[$name]

      file { $this_module_dir:
        ensure  => directory,
        source  => $sourcedir,
        recurse => remote,
        ignore  => $ignore,
      }

      file { "${this_module_dir}/${name}.te":
        ensure => file,
        source => "${sourcedir}/${name}.te",
      }

      exec { "${name}-makemod":
        command     => 'make -f /usr/share/selinux/devel/Makefile',
        refreshonly => true,
      }

      selmodule { $name:
        ensure        => present,
        selmodulepath => $compiled_pp,
        syncversion   => true,
      }

      # Make sure our module is not disabled
      exec { "${name}-enable":
        command => "semodule -e ${name}",
        onlyif  => "test -f ${active_pp}.disabled",
      }
    }
    enabled: {
      exec { "${name}-enabled":
        command => "semodule -e ${name}",
        onlyif  => "test -f ${active_pp}.disabled",
      }
    }
    disabled: {
      exec { "${name}-disabled":
        command => "semodule -d ${name}",
        onlyif  => "test -f ${active_pp}",
      }
    }
    absent: {
      selmodule { $name:
        ensure => $ensure,
      }
      file { $this_module_dir:
        ensure => absent,
        source => $sourcedir,
        purge  => true,
        force  => true,
      }
    }
    default: {
      fail("Selinux::Module: Invalid status: ${ensure}")
    }
  }
}
