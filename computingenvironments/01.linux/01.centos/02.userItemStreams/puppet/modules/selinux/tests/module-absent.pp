selinux::module { 'rsynclocal':
  ensure => 'absent',
  source => 'puppet:///modules/selinux/rsynclocal',
}
