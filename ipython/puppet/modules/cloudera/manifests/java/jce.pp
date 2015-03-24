# == Class: cloudera::java::jce
#
# This class handles installing Oracle Java Cryptography Extension (JCE)
# unlimited strength jurisdiction policy files.
#
# === Parameters:
#
# [*ensure*]
#   Ensure if present or absent.
#   Default: present
#
# === Actions:
#
# Installs the Oracle Java Cryptography Extension (JCE) unlimited strength
# jurisdiction policy files.
#
# === Requires:
#
# Class['cloudera::java']
#
# === Sample Usage:
#
#   class { 'cloudera::java::jce': }
#
# === Authors:
#
# Mike Arnold <mike@razorsedge.org>
#
# === Copyright:
#
# Copyright (C) 2013 Mike Arnold, unless otherwise noted.
#
class cloudera::java::jce (
  $ensure      = $cloudera::params::ensure
) inherits cloudera::params {
  case $ensure {
    /(present)/: {
      $file_ensure = 'present'
    }
    /(absent)/: {
      $file_ensure = 'absent'
    }
    default: {
      fail('ensure parameter must be present or absent')
    }
  }

  File {
    require => Class['cloudera::java'],
  }

  file { '/usr/java/default/jre/lib/security/README.txt':
    ensure => $file_ensure,
    source => "puppet:///modules/${module_name}/jce/README.txt",
    mode   => '0644',
    owner  => 'root',
    group  => 'root',
  }

  file { '/usr/java/default/jre/lib/security/local_policy.jar':
    ensure => $file_ensure,
    source => "puppet:///modules/${module_name}/jce/local_policy.jar",
    mode   => '0644',
    owner  => 'root',
    group  => 'root',
  }

  file { '/usr/java/default/jre/lib/security/US_export_policy.jar':
    ensure => $file_ensure,
    source => "puppet:///modules/${module_name}/jce/US_export_policy.jar",
    mode   => '0644',
    owner  => 'root',
    group  => 'root',
  }
}
