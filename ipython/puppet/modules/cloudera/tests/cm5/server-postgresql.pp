class { 'cloudera::cm5::repo': } ->
class { 'cloudera::java5': } ->
class { 'cloudera::cm5::server':
  db_type => 'postgresql',
  db_user => 'postgres',
  db_pass => '',
  db_port => '5432',
}

include '::postgresql::server'
#class { 'cloudera':
#  cm_server_host   => 'localhost',
#  install_cmserver => true,
#  db_type          => 'postgresql',
#}
