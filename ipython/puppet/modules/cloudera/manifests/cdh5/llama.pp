# == Class: cloudera::cdh5::llama
#
# This class installes Llama.
#
# === Parameters:
#
# === Actions:
#
# === Requires:
#
# === Sample Usage:
#
#   class { 'cloudera::cdh5::llama': }
#
# === Authors:
#
# Mike Arnold <mike@razorsedge.org>
#
# === Copyright:
#
# Copyright (C) 2014 Mike Arnold, unless otherwise noted.
#
class cloudera::cdh5::llama {
  package { 'llama':
    ensure => 'present',
    tag    => 'cloudera-cdh5',
  }
}
