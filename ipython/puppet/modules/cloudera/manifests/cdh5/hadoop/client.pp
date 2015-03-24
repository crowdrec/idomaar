# == Class: cloudera::cdh5::hadoop::client
#
# This class handles installing the Hadoop client packages.
#
# === Parameters:
#
# === Actions:
#
# === Requires:
#
# === Sample Usage:
#
#   class { 'cloudera::cdh5::hadoop::client': }
#
# === Authors:
#
# Mike Arnold <mike@razorsedge.org>
#
# === Copyright:
#
# Copyright (C) 2013 Mike Arnold, unless otherwise noted.
#
class cloudera::cdh5::hadoop::client {
  package { 'hadoop-client':
    ensure => 'present',
    tag    => 'cloudera-cdh5',
  }
}
