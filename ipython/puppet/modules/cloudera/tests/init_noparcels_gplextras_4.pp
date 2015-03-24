class { 'cloudera':
  cm_server_host => 'localhost',
  use_parcels    => false,
  install_lzo    => true,
  cdh_version    => '4',
}
