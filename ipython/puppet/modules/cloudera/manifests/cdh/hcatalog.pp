# == Class: cloudera::cdh::hcatalog
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
#   class { 'cloudera::cdh::hcatalog': }
#
# === Authors:
#
# Mike Arnold <mike@razorsedge.org>
#
# === Copyright:
#
# Copyright (C) 2013 Mike Arnold, unless otherwise noted.
#
class cloudera::cdh::hcatalog {
  package { 'hcatalog':
    ensure => 'present',
    tag    => 'cloudera-cdh4',
  }

  package { 'webhcat':
    ensure => 'present',
    tag    => 'cloudera-cdh4',
  }
}
