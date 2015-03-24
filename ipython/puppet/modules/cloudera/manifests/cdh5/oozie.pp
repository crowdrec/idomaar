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

class cloudera::cdh5::oozie {
  anchor { 'cloudera::cdh5::oozie::begin': }
  anchor { 'cloudera::cdh5::oozie::end': }

  class { 'cloudera::cdh5::oozie::client':
#    ensure      => $ensure,
#    autoupgrade => $autoupgrade,
    require => Anchor['cloudera::cdh5::oozie::begin'],
    before  => Anchor['cloudera::cdh5::oozie::end'],
  }

  package { 'oozie':
    ensure => 'present',
    tag    => 'cloudera-cdh5',
  }

  service { 'oozie':
#   ensure  => 'stopped',
    enable  => false,
    require => Package['oozie'],
  }
}
