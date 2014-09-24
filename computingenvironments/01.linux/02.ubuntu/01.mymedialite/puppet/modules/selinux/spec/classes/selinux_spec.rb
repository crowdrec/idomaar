require 'spec_helper'

describe 'selinux' do
  let(:title) { 'selinux' }

  modes = [ 'enforcing', 'permissive', 'disabled' ]
  modes.each do |current_mode|
    modes.each do |param_mode|
      describe "going from #{current_mode} to #{param_mode}" do 
        let(:params) {{ :mode => param_mode }}
        case current_mode
        when 'enforcing', 'permissive'
          let(:facts) { {
              :osfamily               => 'RedHat',
              :operatingsystemrelease => '6.4',
              :selinux_current_mode   => current_mode,
          } }
        when 'disabled'
          let(:facts) { {
              :osfamily               => 'RedHat',
              :operatingsystemrelease => '6.4',
              :selinux                => 'false',
          } }
        end

        it { should create_class('selinux') }
        it { should create_class('selinux::params') }
        it { should create_class('selinux::config') }
        it { should create_package('libselinux-utils') }
        it { should create_file('/etc/selinux/config')\
          .with_content(/^SELINUX=#{param_mode}$/) }
        if current_mode != param_mode
          # we have to exec setenforce
          if  current_mode != 'disabled'  and  param_mode != 'disabled' 
            it { should create_exec("setenforce #{param_mode}")\
            .with_command("setenforce #{param_mode}") }
          else
            it { should create_notify('change')\
              .with_message(/A reboot is required to change/) }
            it { should_not create_exec("setenforce #{param_mode}") }
            if current_mode == 'enforcing' and param_mode == 'disabled'
              it { should create_exec('setenforce permissive') }
            end
          end
        end
      end
    end
  end
end
