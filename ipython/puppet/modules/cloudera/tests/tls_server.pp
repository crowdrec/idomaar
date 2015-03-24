# The node that will be the CM server may use this declaration:
class { 'cloudera':
  cm_server_host => $::fqdn,
  use_tls        => true,
  use_parcels    => true,
} ->
class { 'cloudera::java::jce': } ->
class { 'cloudera::cm::server':
  use_tls      => true,
  server_keypw => 'myPassWord',
}
file { '/etc/pki/tls/certs/cloudera_manager.crt':
  ensure => present,
  source => 'puppet:///modules/cloudera/cloudera_manager_chain.crt',
  mode   => '0644',
  owner  => 'root',
  group  => 'root',
  before => Class['cloudera::cm'],
}
file { '/etc/pki/tls/certs/cloudera_manager-ca.crt':
  ensure => present,
  source => 'puppet:///modules/cloudera/cloudera_manager-ca.crt',
  mode   => '0644',
  owner  => 'root',
  group  => 'root',
  before => Class['cloudera::cm'],
}
file { "/etc/pki/tls/certs/${::fqdn}-cloudera_manager.crt":
  ensure => present,
  source => "puppet:///modules/cloudera/${::fqdn}-cloudera_manager.crt",
  mode   => '0644',
  owner  => 'root',
  group  => 'root',
  before => Class['cloudera::cm::server'],
}
file { "/etc/pki/tls/private/${::fqdn}-cloudera_manager.key":
  ensure => present,
  source => "puppet:///modules/cloudera/${::fqdn}-cloudera_manager.key",
  mode   => '0400',
  owner  => 'root',
  group  => 'root',
  before => Class['cloudera::cm::server'],
}
