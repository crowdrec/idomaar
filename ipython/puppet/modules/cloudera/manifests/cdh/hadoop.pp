#
#  Copyright (c) 2011, Cloudera, Inc. All Rights Reserved.
#
#  Cloudera, Inc. licenses this file to you under the Apache License,
#  Version 2.0 (the "License"). You may not use this file except in
#  compliance with the License. You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  This software is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
#  CONDITIONS OF ANY KIND, either express or implied. See the License for
#  the specific language governing permissions and limitations under the
#  License.
#

class cloudera::cdh::hadoop {
  anchor { 'cloudera::cdh::hadoop::begin': }
  anchor { 'cloudera::cdh::hadoop::end': }

  class { 'cloudera::cdh::hadoop::client':
#    ensure      => $ensure,
#    autoupgrade => $autoupgrade,
    require => Anchor['cloudera::cdh::hadoop::begin'],
    before  => Anchor['cloudera::cdh::hadoop::end'],
  }

  package { 'hadoop':
    ensure => 'present',
    tag    => 'cloudera-cdh4',
  }

  package { 'hadoop-hdfs':
    ensure => 'present',
    tag    => 'cloudera-cdh4',
  }

  package { 'hadoop-httpfs':
    ensure => 'present',
    tag    => 'cloudera-cdh4',
    notify => Exec['service hadoop-httpfs stop'],
  }

  package { 'hadoop-mapreduce':
    ensure => 'present',
    tag    => 'cloudera-cdh4',
  }

  package { 'hadoop-yarn':
    ensure => 'present',
    tag    => 'cloudera-cdh4',
  }

  package { 'hadoop-0.20-mapreduce':
    ensure => 'present',
    tag    => 'cloudera-cdh4',
  }

  exec { 'service hadoop-httpfs stop':
    path        => '/bin:/usr/bin:/sbin:/usr/sbin',
    refreshonly => true,
  }

  service { 'hadoop-httpfs':
#    ensure    => 'stopped',
    enable    => false,
    hasstatus => true,
    require   => Package['hadoop-httpfs'],
  }
}
