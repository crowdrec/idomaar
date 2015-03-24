class { 'cloudera::cm::repo': } ->
class { 'cloudera::java': } ->
class { 'cloudera::cm::server': }

#class { 'cloudera':
#  cm_server_host   => 'localhost',
#  install_cmserver => true,
#}
