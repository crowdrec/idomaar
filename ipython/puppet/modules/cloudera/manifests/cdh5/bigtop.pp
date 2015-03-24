# == Class: cloudera::cdh5::bigtop
#
# This class installs the BigTop packages.
#
# === Parameters:
#
# === Actions:
#
# === Requires:
#
# === Sample Usage:
#
#   class { 'cloudera::cdh5::bigtop': }
#
# === Authors:
#
# Mike Arnold <mike@razorsedge.org>
#
# === Copyright:
#
# Copyright (C) 2013 Mike Arnold, unless otherwise noted.
#
class cloudera::cdh5::bigtop {
  package { 'bigtop-jsvc':
    ensure => 'present',
    tag    => 'cloudera-cdh5',
  }

  package { 'bigtop-tomcat':
    ensure => 'present',
    tag    => 'cloudera-cdh5',
  }

  package { 'bigtop-utils':
    ensure => 'present',
    tag    => 'cloudera-cdh5',
  }
}
