# == Class: cloudera::cdh5::search::mapreduce
#
# This class handles installing the Cloudera Search SolrCloud.
#
# === Parameters:
#
# === Actions:
#
# === Requires:
#
# === Sample Usage:
#
#   class { 'cloudera::cdh5::search::mapreduce': }
#
# === Authors:
#
# Mike Arnold <mike@razorsedge.org>
#
# === Copyright:
#
# Copyright (C) 2014 Mike Arnold, unless otherwise noted.
#
class cloudera::cdh5::search::mapreduce {
  package { 'solr-mapreduce':
    ensure => 'present',
    tag    => 'cloudera-cdh5',
  }
}
