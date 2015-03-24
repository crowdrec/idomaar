# == Class: cloudera::cdh::sentry
#
# This class installes Sqoop2.
#
# === Parameters:
#
# === Actions:
#
# === Requires:
#
# === Sample Usage:
#
#   class { 'cloudera::cdh::sentry': }
#
# === Authors:
#
# Mike Arnold <mike@razorsedge.org>
#
# === Copyright:
#
# Copyright (C) 2014 Mike Arnold, unless otherwise noted.
#
class cloudera::cdh::sentry {
  package { 'sentry':
    ensure => 'present',
    tag    => 'cloudera-cdh4',
  }
}
