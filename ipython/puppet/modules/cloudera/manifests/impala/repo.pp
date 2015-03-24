# == Class: cloudera::impala::repo
#
# This class handles installing the Cloudera Impala software repositories.
#
# === Parameters:
#
# [*ensure*]
#   Ensure if present or absent.
#   Default: present
#
# [*reposerver*]
#   URI of the YUM server.
#   Default: http://archive.cloudera.com
#
# [*repopath*]
#   The path to add to the $reposerver URI.
#   Only set this if your platform is not supported or you know what you are
#   doing.
#   Default: auto-set, platform specific
#
# [*version*]
#   The version of Cloudera Impala to install.
#   Default: 1
#
# [*proxy*]
#   The URL to the proxy server for the YUM repositories.
#   Default: absent
#
# [*proxy_username*]
#   The username for the YUM proxy.
#   Default: absent
#
# [*proxy_password*]
#   The password for the YUM proxy.
#   Default: absent
#
# === Actions:
#
# Installs YUM repository configuration files.
#
# === Requires:
#
# Nothing.
#
# === Sample Usage:
#
#   class { 'cloudera::impala::repo':
#     version => '4.1',
#   }
#
# === Authors:
#
# Mike Arnold <mike@razorsedge.org>
#
# === Copyright:
#
# Copyright (C) 2014 Mike Arnold, unless otherwise noted.
#
class cloudera::impala::repo (
  $ensure         = $cloudera::params::ensure,
  $reposerver     = $cloudera::params::ci_reposerver,
  $repopath       = $cloudera::params::ci_repopath,
  $version        = $cloudera::params::ci_version,
  $aptkey         = $cloudera::params::ci_aptkey,
  $proxy          = $cloudera::params::proxy,
  $proxy_username = $cloudera::params::proxy_username,
  $proxy_password = $cloudera::params::proxy_password
) inherits cloudera::params {
  case $ensure {
    /(present)/: {
      $enabled = '1'
    }
    /(absent)/: {
      $enabled = '0'
    }
    default: {
      fail('ensure parameter must be present or absent')
    }
  }

  case $::operatingsystem {
    'CentOS', 'RedHat', 'OEL', 'OracleLinux': {
      yumrepo { 'cloudera-impala':
        descr          => 'Impala',
        enabled        => $enabled,
        gpgcheck       => 1,
        gpgkey         => "${reposerver}${repopath}RPM-GPG-KEY-cloudera",
        baseurl        => "${reposerver}${repopath}${version}/",
        priority       => $cloudera::params::yum_priority,
        protect        => $cloudera::params::yum_protect,
        proxy          => $proxy,
        proxy_username => $proxy_username,
        proxy_password => $proxy_password,
      }

      file { '/etc/yum.repos.d/cloudera-impala.repo':
        ensure => 'file',
        owner  => 'root',
        group  => 'root',
        mode   => '0644',
      }

      Yumrepo['cloudera-impala'] -> Package<|tag == 'cloudera-impala'|>
    }
    'SLES': {
      zypprepo { 'cloudera-impala':
        descr       => 'Impala',
        enabled     => $enabled,
        gpgcheck    => 1,
        gpgkey      => "${reposerver}${repopath}RPM-GPG-KEY-cloudera",
        baseurl     => "${reposerver}${repopath}${version}/",
        autorefresh => 1,
        priority    => $cloudera::params::yum_priority,
      }

      file { '/etc/zypp/repos.d/cloudera-impala.repo':
        ensure => 'file',
        owner  => 'root',
        group  => 'root',
        mode   => '0644',
      }

      Zypprepo['cloudera-impala'] -> Package<|tag == 'cloudera-impala'|>
    }
    'Debian', 'Ubuntu': {
      include '::apt'

      apt::source { 'cloudera-impala':
        location     => "${reposerver}${repopath}",
        release      => "${::lsbdistcodename}-impala${version}",
        repos        => 'contrib',
        key          => $aptkey,
        key_source   => "${reposerver}${repopath}archive.key",
        architecture => $cloudera::params::architecture,
      }

      Apt::Source['cloudera-impala'] -> Package<|tag == 'cloudera-impala'|>
    }
    default: { }
  }
}
