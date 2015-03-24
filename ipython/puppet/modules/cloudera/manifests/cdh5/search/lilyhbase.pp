# == Class: cloudera::cdh5::search::lilyhbase
#
# This class handles installing the Cloudera Search Lily HBase Indexer.
#
# === Parameters:
#
# === Actions:
#
# === Requires:
#
# === Sample Usage:
#
#   class { 'cloudera::cdh5::search::lilyhbase': }
#
# === Authors:
#
# Mike Arnold <mike@razorsedge.org>
#
# === Copyright:
#
# Copyright (C) 2014 Mike Arnold, unless otherwise noted.
#
class cloudera::cdh5::search::lilyhbase {
  package { 'hbase-solr':
    ensure => 'present',
    tag    => 'cloudera-cdh5',
  }

#  package { 'hbase-solr-doc':
#    ensure => 'present',
#    tag    => 'cloudera-cdh5',
#  }
}
