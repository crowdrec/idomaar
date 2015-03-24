# == Class: cloudera::cdh5::hcatalog
#
# This class installes HCatalog.
#
# === Parameters:
#
# === Actions:
#
# === Requires:
#
# === Sample Usage:
#
#   class { 'cloudera::cdh5::hcatalog': }
#
# === Authors:
#
# Mike Arnold <mike@razorsedge.org>
#
# === Copyright:
#
# Copyright (C) 2013 Mike Arnold, unless otherwise noted.
#
class cloudera::cdh5::hcatalog {
  package { 'hcatalog':
    ensure => 'absent',
    tag    => 'cloudera-cdh5',
  }

  package { 'webhcat':
    ensure => 'absent',
    tag    => 'cloudera-cdh5',
  }
  package { 'hive-hcatalog':
    ensure => 'present',
    tag    => 'cloudera-cdh5',
  }

  package { 'hive-webhcat':
    ensure => 'present',
    tag    => 'cloudera-cdh5',
  }
}
