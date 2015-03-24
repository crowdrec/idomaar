class { 'cloudera':
  cm_server_host => 'smhost.example.com',
}
class { 'cloudera::cdh::hue': }
class { 'cloudera::cdh::mahout': }
class { 'cloudera::cdh::sqoop': }
# Install Oozie WebUI support (optional):
#class { 'cloudera::cdh::oozie::ext': }
# Install MySQL support (optional):
#class { 'cloudera::cdh::hue::mysql': }
#class { 'cloudera::cdh::oozie::mysql': }
