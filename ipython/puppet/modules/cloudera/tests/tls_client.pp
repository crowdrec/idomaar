# The node that will be the CM agent may use this declaration:
class { 'cloudera':
  cm_server_host => 'some.other.host',
  use_tls        => true,
  use_parcels    => true,
} ->
class { 'cloudera::java::jce': }
file { '/etc/pki/tls/certs/cloudera_manager.crt':
  ensure => present,
  source => 'puppet:///modules/cloudera/cloudera_manager_chain.crt',
  mode   => '0644',
  owner  => 'root',
  group  => 'root',
  before => Class['cloudera::cm'],
}
