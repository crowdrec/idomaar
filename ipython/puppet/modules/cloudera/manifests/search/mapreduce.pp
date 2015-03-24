# == Class: cloudera::search::mapreduce
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
#   class { 'cloudera::search::mapreduce': }
#
# === Authors:
#
# Mike Arnold <mike@razorsedge.org>
#
# === Copyright:
#
# Copyright (C) 2014 Mike Arnold, unless otherwise noted.
#
class cloudera::search::mapreduce {
  package { 'solr-mapreduce':
    ensure => 'present',
    tag    => 'cloudera-search',
  }
}
