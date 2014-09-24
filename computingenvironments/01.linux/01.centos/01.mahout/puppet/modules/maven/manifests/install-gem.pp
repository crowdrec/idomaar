define maven::install-gem ($version = '') {

  warning('maven::install-gem is deprecated, use maven::install_gem')

  exec { "gem $name $version":
    path        => '/usr/bin:/opt/ruby/bin',
    environment => "JAVA_HOME=$maven::java_home",
    command     => "gem install $name --version $version --no-rdoc --no-ri",
    unless      => "gem query -i --name-matches $name --version $version",
    logoutput   => true,
  }
}
