# == Class: cloudera::gplextras5
#
# This class handles installing the Cloudera GPL Extras.
#
# === Parameters:
#
# [*ensure*]
#   Ensure if present or absent.
#   Default: present
#
# [*autoupgrade*]
#   Upgrade package automatically, if there is a newer version.
#   Default: false
#
# === Actions:
#
# Installs GPL Extras.
#
# === Requires:
#
# Nothing.
#
# === Sample Usage:
#
#   class { 'cloudera::gplextras5': }
#
# === Authors:
#
# Mike Arnold <mike@razorsedge.org>
#
# === Copyright:
#
# Copyright (C) 2014 Mike Arnold, unless otherwise noted.
#
class cloudera::gplextras5 (
  $ensure         = $cloudera::params::ensure,
  $autoupgrade    = $cloudera::params::safe_autoupgrade
) inherits cloudera::params {
  # Validate our booleans
  validate_bool($autoupgrade)

  if ($::operatingsystem in [ 'CentOS', 'RedHat', 'OEL', 'OracleLinux' ]) and ($cloudera::params::majdistrelease == 5) {
    require '::epel'
  }

  package { 'hadoop-lzo':
    ensure => 'present',
    tag    => 'cloudera-gplextras5',
  }

  package { 'hadoop-lzo-mr1':
    ensure => 'present',
    tag    => 'cloudera-gplextras5',
  }

  package { 'impala-lzo':
    ensure => 'present',
    tag    => 'cloudera-gplextras5',
  }
}
