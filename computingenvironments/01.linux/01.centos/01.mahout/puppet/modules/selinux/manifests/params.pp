# == Class: selinux::params
#
#  This class provides default parameters for the selinux class
#
# === Example
#
# file { "$selinux::params::modules_dir"/foobar/foobar.te":
#   ensure => present,
# }
#
class selinux::params (
  $modules_dir = "${::settings::vardir}/selinux"
  ) {
  case $::osfamily {
    'RedHat': {
      if $::operatingsystemrelease < '7' {
        $selinux_policy_devel = 'selinux-policy'
      } else {
        $selinux_policy_devel = 'selinux-policy-devel'
      }
    }
    default: {
        fail('Unsupported OS')
    }
  }
}
