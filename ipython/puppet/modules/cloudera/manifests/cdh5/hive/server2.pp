# == Class: cloudera::cdh5::hive::server2
#
# This class handles installing the Hive Metastore service.
#
# === Parameters:
#
# === Actions:
#
# === Requires:
#
# === Sample Usage:
#
#   class { 'cloudera::cdh5::hive::server2': }
#
# === Authors:
#
# Mike Arnold <mike@razorsedge.org>
#
# === Copyright:
#
# Copyright (C) 2013 Mike Arnold, unless otherwise noted.
#
class cloudera::cdh5::hive::server2 {
  package { 'hive-server2':
    ensure => present,
    tag    => 'cloudera-cdh5',
  }

  service { 'hive-server2':
    ensure     => running,
    enable     => true,
    hasstatus  => true,
    hasrestart => true,
    require    => Package['hive-server2'],
  }
}
