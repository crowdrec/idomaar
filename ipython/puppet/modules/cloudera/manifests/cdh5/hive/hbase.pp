# == Class: cloudera::cdh5::hive::hbase
#
# This class handles installing the Hive HBase integration.
#
# === Parameters:
#
# === Actions:
#
# === Requires:
#
# === Sample Usage:
#
#   class { 'cloudera::cdh5::hive::hbase': }
#
# === Authors:
#
# Mike Arnold <mike@razorsedge.org>
#
# === Copyright:
#
# Copyright (C) 2013 Mike Arnold, unless otherwise noted.
#
class cloudera::cdh5::hive::hbase {
  package { 'hive-hbase':
    ensure => present,
    tag    => 'cloudera-cdh5',
  }
}
