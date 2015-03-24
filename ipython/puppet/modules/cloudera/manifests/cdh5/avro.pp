# == Class: cloudera::cdh5::avro
#
# This class installes Avro Tools.
#
# === Parameters:
#
# === Actions:
#
# === Requires:
#
# === Sample Usage:
#
#   class { 'cloudera::cdh5::avro': }
#
# === Authors:
#
# Mike Arnold <mike@razorsedge.org>
#
# === Copyright:
#
# Copyright (C) 2014 Mike Arnold, unless otherwise noted.
#
class cloudera::cdh5::avro {
  package { 'avro-tools':
    ensure => 'present',
    tag    => 'cloudera-cdh5',
  }
}
