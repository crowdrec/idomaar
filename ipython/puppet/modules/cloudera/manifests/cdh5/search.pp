# == Class: cloudera::cdh5::search
#
# This class handles installing the Cloudera Search.
#
# === Parameters:
#
# [*ensure*]
#   Ensure if present or absent.
#   Default: present
#
# [*autoupgrade*]
#   Upgrade package automatically, if there is a newer version.
#   Default: false
#
# [*service_ensure*]
#   Ensure if service is running or stopped.
#   Default: running
#
# === Actions:
#
# Installs Search.
#
# === Requires:
#
# Nothing.
#
# === Sample Usage:
#
#   class { 'cloudera::cdh5::search': }
#
# === Authors:
#
# Mike Arnold <mike@razorsedge.org>
#
# === Copyright:
#
# Copyright (C) 2014 Mike Arnold, unless otherwise noted.
#
class cloudera::cdh5::search (
  $ensure         = $cloudera::params::ensure,
  $autoupgrade    = $cloudera::params::safe_autoupgrade,
  $service_ensure = $cloudera::params::service_ensure
) inherits cloudera::params {
  # Validate our booleans
  validate_bool($autoupgrade)

  package { 'solr-server':
    ensure => 'present',
    tag    => 'cloudera-cdh5',
  }

  service { 'solr-server':
#   ensure    => 'stopped',
    enable    => false,
    hasstatus => true,
    require   => Package['solr-server'],
  }
}
