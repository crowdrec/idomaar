# == Class: cloudera::cdh5::kite
#
# This class handles installing the Kite Software Development Kit.
#
# === Parameters:
#
# === Actions:
#
# === Requires:
#
# === Sample Usage:
#
#   class { 'cloudera::cdh5::kite': }
#
# === Authors:
#
# Mike Arnold <mike@razorsedge.org>
#
# === Copyright:
#
# Copyright (C) 2014 Mike Arnold, unless otherwise noted.
#
class cloudera::cdh5::kite {
  package { 'kite':
    ensure => 'present',
    tag    => 'cloudera-cdh5',
  }
}
