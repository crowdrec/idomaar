require 'spec_helper'

# $stdout.puts self.catalogue.to_yaml

active_modules = "/etc/selinux/targeted/modules/active/modules"
describe 'selinux::module', :type => :define do
  let(:title) { 'selinux::module' }

  describe "loading module" do
    modname = 'rsynclocal'
    modules_dir = '/var/lib/puppet/selinux'
    this_module_dir = "#{modules_dir}/#{modname}"
    source = "puppet:///modules/selinux/#{modname}"
    ignore = [ 'CVS', '.svn' ]
    let(:title) { modname }
    let(:params) {{
      :source      => source,
      :modules_dir => modules_dir,
      :ignore      =>  ignore
    }}
    let(:facts) { {
        :osfamily      => 'RedHat',
        :operatingsystemrelease => '6.4'
    } }

    it { should create_class('selinux') }
    it { should create_class('selinux::params') }
    it { should create_class('selinux::config') }
    it { should create_class('selinux::install') }
    it { should create_package('policycoreutils') }
    it { should create_package('checkpolicy') }
    it { should create_package('selinux-policy') }
    it { should create_package('make') }
    it { should create_selinux__module(modname) }
    it { should create_file("#{this_module_dir}")\
      .with(
        :ensure  => 'directory',
        :recurse => 'remote',
        :source  => source,
        :ignore  => ignore
      ) } 
    it { should create_file("#{this_module_dir}/#{modname}.te")\
      .with(
        :ensure  => 'file',
        :source  => "#{source}/#{modname}.te"
      ) } 
    it { should create_exec("#{modname}-makemod")\
      .with(
        :command     => 'make -f /usr/share/selinux/devel/Makefile',
        :refreshonly => 'true',
        :cwd         => this_module_dir
      ) }
    it { should create_selmodule(modname)\
      .with(
        :ensure        => 'present',
        :selmodulepath => "#{this_module_dir}/#{modname}.pp",
        :syncversion   => 'true'
      )}
    it { should create_exec("#{modname}-enable")\
      .with(
        :command => "semodule -e #{modname}",
        :onlyif  => "test -f #{active_modules}/#{modname}.pp.disabled"
      ) }
  end
  [ '4.5', '5.8', '6.4', '7.0', '19' ].each do | osrelease |
    describe "checking package installation: #{osrelease}" do
      modname = 'rsynclocal'
      source = "puppet:///modules/selinux/#{modname}"
      modules_dir = '/var/lib/puppet/selinux'
      let(:title) { modname }
      let(:params) {{
        :source      => source,
        :modules_dir => modules_dir,
      }}
      let(:facts) { {
          :osfamily      => 'RedHat',
          :operatingsystemrelease => osrelease,
      } }
      if osrelease.to_f < 7
        it { should create_package('selinux-policy') }
      else
        it { should create_package('selinux-policy-devel') }
      end
    end
  end
  # disable, enable
  [ 'enabled', 'disabled' ].each do | ensured |
    describe "check with #{ensured} parameter" do
      modname = 'rsynclocal'
      source = "puppet:///modules/selinux/#{modname}"
      modules_dir = '/var/lib/puppet/selinux'
      case ensured
      when 'enabled'
        opt = '-e'
        tested_file = "#{active_modules}/#{modname}.pp.disabled"
      when 'disabled'
        opt = '-d'
        tested_file = "#{active_modules}/#{modname}.pp"
      end
      let(:title) { modname }
      let(:params) {{
        :source      => source,
        :modules_dir => modules_dir,
        :ensure      => ensured
      }}
      let(:facts) { {
          :osfamily      => 'RedHat',
          :operatingsystemrelease => '7',
      } }
      it { should create_exec("#{modname}-#{ensured}")\
        .with(
          :command => "semodule #{opt} #{modname}",
          :onlyif  => "test -f #{tested_file}"
        )}
    end
  end
  # absent
  describe "check with absent" do 
    modname = 'rsynclocal'
    source = "puppet:///modules/selinux/#{modname}"
    modules_dir = '/var/lib/puppet/selinux'
    let(:title) { modname }
    let(:params) {{
      :ensure      => 'absent',
      :source      => source,
      :modules_dir => modules_dir
    }}
    let(:facts) { {
        :osfamily      => 'RedHat',
        :operatingsystemrelease => '7',
    } }
    it { should create_file("#{modules_dir}/#{modname}") }
    it {
      should create_file(modules_dir + '/' + modname)\
      .with(
        :ensure => 'absent',
        :purge  => 'true',
        :force  => 'true'
    )}
  end
  # source
  [
    nil,
    'https://github.com/modules/selinux/mod.te',
    'puppet:///modules/selinux/mod.te',
    'puppet:///modules/selinux/',
    'file:///usr/local/share/selinux/rsynclocal',
    'puppet:///modules/selinux/rsynclocal/rsynclocal.te',
    'puppet:///modules/selinux/httpd_rotatelogs/httpd_rotatelogs.te',
    'puppet:///modules/selinux/httpd_rotatelogs',
    'puppet:///modules/selinux/rsynclocal',
    'puppet:///modules/selinux/rsynclocal/'
  ].each do | source |
    describe "source parameter check #{source}" do
      modname = 'rsynclocal'
      modules_dir = '/var/lib/puppet/selinux'
      let(:title) { modname }
      if source == nil
        let(:params) {{
          :modules_dir => modules_dir,
        }}
      else
        let(:params) {{
          :source      => source,
          :modules_dir => modules_dir,
        }}
      end
      let(:facts) {{
          :osfamily      => 'RedHat',
          :operatingsystemrelease => '6.4',
      }}
      case source
      when nil
        #no source, let's take the default one
        it { should create_file(modules_dir + "/#{modname}/#{modname}.te")\
        .with_source("puppet:///modules/selinux/#{modname}/#{modname}.te") }
      when /^puppet:.*\.te$/
        # invalid source: we want' a directory
        it { expect { should include_class('selinux::install') }.to\
            raise_error(Puppet::Error,
                        /Invalid source parameter, expecting a directory/) }
      when /^puppet:\/\/\/modules\/\w+\/\w+/ , /^file:\/\/\/.*$/
        # valid source
        it { should create_file(modules_dir + "/#{modname}/#{modname}.te")\
        .with_source(source + "/#{modname}.te") }
      else
        it { expect { should include_class('selinux::install') }.to\
            raise_error(Puppet::Error, /Invalid source parameter/) }
      end
    end
  end
end
