# Class:
#
# Description
#
# Parameters:
#
# Actions:
#
# Requires:
#
# Sample Usage:
#

selinux::module { 'rsynclocal':
  ensure => 'present',
  source => 'puppet:///modules/selinux/rsynclocal',
}
