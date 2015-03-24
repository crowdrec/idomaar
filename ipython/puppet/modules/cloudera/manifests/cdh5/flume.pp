# == Class: cloudera::cdh5::flume
#
# This class installs the Flume NG packages.
#
# === Parameters:
#
# === Actions:
#
# === Requires:
#
# === Sample Usage:
#
#   class { 'cloudera::cdh5::flume': }
#
# === Authors:
#
# Mike Arnold <mike@razorsedge.org>
#
# === Copyright:
#
# Copyright (C) 2013 Mike Arnold, unless otherwise noted.
#
class cloudera::cdh5::flume {
  package { 'flume-ng':
    ensure => 'present',
    tag    => 'cloudera-cdh5',
  }

  case $::operatingsystem {
    'CentOS', 'RedHat', 'OEL', 'OracleLinux', 'SLES', 'Debian': {
      service { 'flume-ng':
#        ensure     => 'running',
        enable     => false,
        hasstatus  => false,
        hasrestart => true,
        require    => Package['flume-ng'],
      }
    }
    default: { }
  }
}
