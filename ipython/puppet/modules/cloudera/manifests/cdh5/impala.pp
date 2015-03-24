# == Class: cloudera::cdh5::impala
#
# This class handles installing the Cloudera Impala.
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
# Installs Impala.
#
# === Requires:
#
# Nothing.
#
# === Sample Usage:
#
#   class { 'cloudera::cdh5::impala': }
#
# === Authors:
#
# Mike Arnold <mike@razorsedge.org>
#
# === Copyright:
#
# Copyright (C) 2013 Mike Arnold, unless otherwise noted.
#
class cloudera::cdh5::impala (
  $ensure         = $cloudera::params::ensure,
  $autoupgrade    = $cloudera::params::safe_autoupgrade,
  $service_ensure = $cloudera::params::service_ensure
) inherits cloudera::params {
  # Validate our booleans
  validate_bool($autoupgrade)

  package { 'impala':
    ensure => 'present',
    tag    => 'cloudera-cdh5',
  }

  package { 'impala-shell':
    ensure => 'present',
    tag    => 'cloudera-cdh5',
  }
}
