# == Class: cloudera::lzo
#
# This class handles installing the native LZO libraries to support Hadoop LZO
# compression.
#
# === Parameters:
#
# [*autoupgrade*]
#   Upgrade package automatically, if there is a newer version.
#   Default: false
#
# === Actions:
#
# Installs native LZO libraries.
#
# === Requires:
#
# EPEL for EL5.
#
# === Sample Usage:
#
#   class { 'cloudera::lzo': }
#
# === Authors:
#
# Mike Arnold <mike@razorsedge.org>
#
# === Copyright:
#
# Copyright (C) 2014 Mike Arnold, unless otherwise noted.
#
class cloudera::lzo (
  $autoupgrade = $cloudera::params::safe_autoupgrade
) inherits cloudera::params {
  # Validate our booleans
  validate_bool($autoupgrade)

  if ($::operatingsystem in [ 'CentOS', 'RedHat', 'OEL', 'OracleLinux' ]) and ($cloudera::params::majdistrelease == 5) {
    require '::epel'
  }

  package { 'lzo':
    ensure => 'present',
    name   => $cloudera::params::lzo_package_name,
  }
}
