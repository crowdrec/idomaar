#!/usr/bin/env rspec

require 'spec_helper'

describe 'cloudera::cdh::flume', :type => 'class' do

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
    context 'CentOS' do
#      let(:params) {{}}
      let :facts do {
        :osfamily        => 'RedHat',
        :operatingsystem => 'CentOS'
      }
      end
      it { should contain_package('flume-ng').with_ensure('present') }
      it { should contain_service('flume-ng').with_enable('false') }
    end

    context 'Ubuntu' do
      let :facts do {
        :osfamily        => 'Debian',
        :operatingsystem => 'Ubuntu'
      }
      end
      it { should_not contain_service('flume-ng') }
    end
  end
end
