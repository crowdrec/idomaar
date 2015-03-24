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

class cloudera::cdh5::hadoop {
  anchor { 'cloudera::cdh5::hadoop::begin': }
  anchor { 'cloudera::cdh5::hadoop::end': }

  class { 'cloudera::cdh5::hadoop::client':
#    ensure      => $ensure,
#    autoupgrade => $autoupgrade,
    require => Anchor['cloudera::cdh5::hadoop::begin'],
    before  => Anchor['cloudera::cdh5::hadoop::end'],
  }

  package { 'hadoop':
    ensure => 'present',
    tag    => 'cloudera-cdh5',
  }

  package { 'hadoop-hdfs':
    ensure => 'present',
    tag    => 'cloudera-cdh5',
  }

  package { 'hadoop-httpfs':
    ensure => 'present',
    tag    => 'cloudera-cdh5',
    notify => Exec['service hadoop-httpfs stop'],
  }

  package { 'hadoop-mapreduce':
    ensure => 'present',
    tag    => 'cloudera-cdh5',
  }

  package { 'hadoop-yarn':
    ensure => 'present',
    tag    => 'cloudera-cdh5',
  }

  package { 'hadoop-0.20-mapreduce':
    ensure => 'present',
    tag    => 'cloudera-cdh5',
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
