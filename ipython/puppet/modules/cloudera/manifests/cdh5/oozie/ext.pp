# == Class: cloudera::cdh5::oozie::ext
#
# This class handles installing the Oozie Web Console.
#
# === Parameters:
#
# [*oozie_ext*]
#   URI of the ext-2.2.zip file required by Oozie in order to enable the WebUI.
#   Default: http://archive.cloudera.com/gplextras/misc/ext-2.2.zip
#
# === Actions:
#
# Downloads and unzips ext-2.2.zip.
#
# === Requires:
#
#   Define['staging::deploy']
#
# === Sample Usage:
#
#   class { 'cloudera::cdh5::oozie::ext': }
#
# === Authors:
#
# Mike Arnold <mike@razorsedge.org>
#
# === Copyright:
#
# Copyright (C) 2013 Mike Arnold, unless otherwise noted.
#
class cloudera::cdh5::oozie::ext (
  $source = $cloudera::params::oozie_ext
) inherits cloudera::params {
  staging::deploy { 'ext-2.2.zip':
    source => $source,
    target => '/usr/lib/oozie/libext',
  }
}
