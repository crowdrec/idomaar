#!/usr/bin/env rspec

require 'spec_helper'

describe 'cloudera::cdh5::hive::metastore', :type => 'class' do

#  context 'on a non-supported operatingsystem' do
#    let :facts do {
#      :osfamily        => 'foo',
#      :operatingsystem => 'bar'
#    }
#    end
#    it 'should fail' do
#      expect {
#        should raise_error(Puppet::Error, /Module cloudera is not supported on bar/)
#      }
#    end
#  end

  context 'on a supported operatingsystem, default parameters' do
    let(:params) {{}}
    let :facts do {
      :osfamily        => 'RedHat',
      :operatingsystem => 'CentOS'
    }
    end
    it { should contain_package('hive-metastore').with_ensure('present') }
    it { should contain_service('hive-metastore').with(
      :ensure     => 'running',
      :enable     => true,
      :hasrestart => true,
      :hasstatus  => true,
      :require    => [ 'Package[hive-metastore]', 'File[/usr/lib/hive/lib/mysql-connector-java.jar]' ]
    )}
    it { should contain_class('mysql::bindings') }
    it { should contain_class('mysql::bindings::java') }
    it { should contain_file('/usr/lib/hive/lib/mysql-connector-java.jar').with(
      :ensure  => 'link',
      :target  => '/usr/share/java/mysql-connector-java.jar',
      :require => 'Class[Mysql::Bindings::Java]'
    )}
  end
end
