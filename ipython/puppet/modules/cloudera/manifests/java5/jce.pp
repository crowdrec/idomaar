# == Class: cloudera::java5::jce
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
# Class['cloudera::java5']
#
# === Sample Usage:
#
#   class { 'cloudera::java5::jce': }
#
# === Authors:
#
# Mike Arnold <mike@razorsedge.org>
#
# === Copyright:
#
# Copyright (C) 2013 Mike Arnold, unless otherwise noted.
#
class cloudera::java5::jce (
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
    require => Class['cloudera::java5'],
  }

  file { '/usr/java/default/jre/lib/security/README.txt':
    ensure => $file_ensure,
    source => "puppet:///modules/${module_name}/UnlimitedJCEPolicy/README.txt",
    mode   => '0644',
    owner  => 'root',
    group  => 'root',
  }

  file { '/usr/java/default/jre/lib/security/local_policy.jar':
    ensure => $file_ensure,
    source => "puppet:///modules/${module_name}/UnlimitedJCEPolicy/local_policy.jar",
    mode   => '0644',
    owner  => 'root',
    group  => 'root',
  }

  file { '/usr/java/default/jre/lib/security/US_export_policy.jar':
    ensure => $file_ensure,
    source => "puppet:///modules/${module_name}/UnlimitedJCEPolicy/US_export_policy.jar",
    mode   => '0644',
    owner  => 'root',
    group  => 'root',
  }
}
