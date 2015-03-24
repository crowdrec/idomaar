# == Class: cloudera::cdh5::crunch
#
# This class installes Apache Crunch.
#
# === Parameters:
#
# === Actions:
#
# === Requires:
#
# === Sample Usage:
#
#   class { 'cloudera::cdh5::crunch': }
#
# === Authors:
#
# Mike Arnold <mike@razorsedge.org>
#
# === Copyright:
#
# Copyright (C) 2014 Mike Arnold, unless otherwise noted.
#
class cloudera::cdh5::crunch {
  package { 'crunch':
    ensure => 'present',
    tag    => 'cloudera-cdh5',
  }
}
