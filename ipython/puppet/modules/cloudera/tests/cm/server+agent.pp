class { 'cloudera':
  cm_server_host   => 'localhost',
  cm_version       => '4',
  install_cmserver => true,
}
