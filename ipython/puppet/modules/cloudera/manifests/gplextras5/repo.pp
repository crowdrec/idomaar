# == Class: cloudera::gplextras5::repo
#
# This class handles installing the Cloudera GPL Extras software repositories.
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
#   The version of Cloudera GPL Extras to install.
#   Default: 5
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
#   class { 'cloudera::gplextras5::repo':
#     version => '4.3.0',
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
class cloudera::gplextras5::repo (
  $ensure         = $cloudera::params::ensure,
  $reposerver     = $cloudera::params::cg_reposerver,
  $repopath       = $cloudera::params::cg5_repopath,
  $version        = $cloudera::params::cg_version,
  $aptkey         = $cloudera::params::cg_aptkey,
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
      yumrepo { 'cloudera-gplextras5':
        descr          => 'Cloudera GPL Extras',
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

      file { '/etc/yum.repos.d/cloudera-gplextras5.repo':
        ensure => 'file',
        owner  => 'root',
        group  => 'root',
        mode   => '0644',
      }

      Yumrepo['cloudera-gplextras5'] -> Package<|tag == 'cloudera-gplextras5'|>
    }
    'SLES': {
      zypprepo { 'cloudera-gplextras5':
        descr       => 'Cloudera GPL Extras',
        enabled     => $enabled,
        gpgcheck    => 1,
        gpgkey      => "${reposerver}${repopath}RPM-GPG-KEY-cloudera",
        baseurl     => "${reposerver}${repopath}${version}/",
        autorefresh => 1,
        priority    => $cloudera::params::yum_priority,
      }

      file { '/etc/zypp/repos.d/cloudera-gplextras5.repo':
        ensure => 'file',
        owner  => 'root',
        group  => 'root',
        mode   => '0644',
      }

      Zypprepo['cloudera-gplextras5'] -> Package<|tag == 'cloudera-gplextras5'|>
    }
    'Debian', 'Ubuntu': {
      include '::apt'

      apt::source { 'cloudera-gplextras5':
        location     => "${reposerver}${repopath}",
        release      => "${::lsbdistcodename}-gplextras${version}",
        repos        => 'contrib',
        key          => $aptkey,
        key_source   => "${reposerver}${repopath}archive.key",
        architecture => $cloudera::params::architecture,
      }

      Apt::Source['cloudera-gplextras5'] -> Package<|tag == 'cloudera-gplextras5'|>
    }
    default: { }
  }
}
