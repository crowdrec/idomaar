# == Class: cloudera::cdh5::hue::plugins
#
# This class installes the HUE plugins.
#
# === Parameters:
#
# === Actions:
#
# === Requires:
#
# === Sample Usage:
#
#   class { 'cloudera::cdh5::hue::plugins': }
#
# === Authors:
#
# Mike Arnold <mike@razorsedge.org>
#
# === Copyright:
#
# Copyright (C) 2013 Mike Arnold, unless otherwise noted.
#
class cloudera::cdh5::hue::plugins {
  package { 'hue-plugins':
    ensure => 'present',
    tag    => 'cloudera-cdh5',
  }

  # CDH 4.1.1 had the required file in hue-plugins. In CDH 4.1.2 said file
  # becomes a symlink to a file in hue-common.
  package { 'hue-common':
    ensure => 'present',
    tag    => 'cloudera-cdh5',
  }
}
