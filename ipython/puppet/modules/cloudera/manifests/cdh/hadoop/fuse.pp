# == Class: cloudera::cdh::hadoop::fuse
#
# This class handles installing the Hadoop HDFS FUSE packages.
#
# === Parameters:
#
# === Actions:
#
# === Requires:
#
# === Sample Usage:
#
#   class { 'cloudera::cdh::hadoop::fuse': }
#
# === Authors:
#
# Mike Arnold <mike@razorsedge.org>
#
# === Copyright:
#
# Copyright (C) 2013 Mike Arnold, unless otherwise noted.
#
class cloudera::cdh::hadoop::fuse {
  package { 'hadoop-hdfs-fuse':
    ensure => 'present',
    tag    => 'cloudera-cdh4',
  }
}
