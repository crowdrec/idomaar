require 'puppetlabs_spec_helper/rake_tasks'

task :default => [:lint, :spec]

desc "build module"
task :buildmodule do
  system('puppet module build')
end

desc "Run all tasks for a release"
task :release => [:spec, :clean, :buildmodule]
