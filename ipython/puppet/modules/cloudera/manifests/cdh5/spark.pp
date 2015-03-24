# == Class: cloudera::cdh5::spark
#
# This class handles installing the Apache Spark.
#
# === Parameters:
#
# === Actions:
#
# === Requires:
#
# === Sample Usage:
#
#   class { 'cloudera::cdh5::spark': }
#
# === Authors:
#
# Mike Arnold <mike@razorsedge.org>
#
# === Copyright:
#
# Copyright (C) 2014 Mike Arnold, unless otherwise noted.
#
class cloudera::cdh5::spark {
  package { 'spark-core':
    ensure => 'present',
    tag    => 'cloudera-cdh5',
  }

  package { 'spark-python':
    ensure => 'present',
    tag    => 'cloudera-cdh5',
  }
}
