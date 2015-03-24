#!/usr/bin/env rspec

require 'spec_helper'

describe 'cloudera::cdh5::hadoop', :type => 'class' do

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
#    let(:params) {{}}
#    let :facts do {
#      :osfamily        => 'RedHat',
#      :operatingsystem => 'CentOS'
#    }
#    end
    it { should contain_class('cloudera::cdh5::hadoop::client') }
    it { should contain_package('hadoop').with_ensure('present') }
    it { should contain_package('hadoop-hdfs').with_ensure('present') }
    it { should contain_package('hadoop-httpfs').with_ensure('present').with_notify('Exec[service hadoop-httpfs stop]') }
    it { should contain_package('hadoop-mapreduce').with_ensure('present') }
    it { should contain_package('hadoop-yarn').with_ensure('present') }
    it { should contain_package('hadoop-0.20-mapreduce').with_ensure('present') }
    it { should contain_service('hadoop-httpfs').with_enable('false') }
    it { should contain_exec('service hadoop-httpfs stop').with_refreshonly('true') }
  end
end
