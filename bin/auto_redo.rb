#!/usr/bin/env ruby

# From /var/log/zuul/debug.log:
#
# 2014-11-11 10:08:06,017 DEBUG zuul.IndependentPipelineManager: 
#  Adding build <Build 47da063b16404fd8ae6c83982780ab0d of a10-neutron-tempest
#  on <Worker Unknown>> of job a10-neutron-tempest to item 
#  <QueueItem 0x7f99ca673250 for <Change 0x7f99caa34b10 133502,3> in check>

# 2014-11-11 10:30:00,730 INFO zuul.Gearman: 
#  Build <gear.Job 0x7f99ca673950 handle: H:127.0.0.1:10314 name: 
#  build:a10-neutron-tempest unique: 47da063b16404fd8ae6c83982780ab0d> complete, 
#  result FAILURE

# 2014-11-11 15:23:14,341 INFO zuul.Gearman: Cancel build 
#  <Build 85e9d6c1d7504d1e8557ed7006653e73 of a10-neutron-tempest 
#  on <Worker Unknown>> for job a10-neutron-tempest


require "filewatch/tail"

class ZuulWatcher

  def initialize()
    @consecutive_failures = 0
    @changes = {}
    @jobs = {}
    @retried = {}
  end

  def pause_jobs()
    puts "TODO: need to implement pause"
  end

  def redo_job(changenum, patchset)
    k = "#{changenum},#{patchset}"

    if @retried[k]
      puts "  FAILED: #{k}, skipping retry; already tried once"
      return
    else
      puts "  FAILED: #{k}, retrying"
    end

    p = "openstack/neutron"
    p = @changes[changenum][:project] unless @changes[changenum].nil?

    cmd="zuul enqueue --trigger gerrit --pipeline check --project #{p} --change #{k}"
    puts "redo_job: #{cmd}"
  #  r = `#{cmd}`
  #  if r.strip() != ''
  #    print "WARNING: zuul enqueue returned: #{r}"
  #  end

    @retried[k] = true
  end

  def watch_file(file_path, &block)
    logger = Logger.new(STDOUT)
    logger.level = Logger::INFO

    since_path = ENV['HOME'] + "/.filewatch.#{File.basename(file_path)}"

    while true
      begin
        t = FileWatch::Tail.new start_new_files_at: :beginning, 
                                sincedb_path: since_path, logger: logger
        t.tail(file_path)
        t.subscribe do |path, line|
          #puts "#{path}: #{line}"
          yield line
        end

      rescue Exception => e
        puts "Watch is about to blow an exception: #{e.inspect}"
        puts e.backtrace
        STDOUT.flush
        sleep 0.1
      end
    end

    # File.open(file_path).each_line do |line|
    #   yield line
    # end
  end

  def watch_loop()

    # watch_file('/var/log/zuul/zuul.log') do |line|
    watch_file('/var/log/zuul/debug.log') do |line|

      puts "LINE #{line}"

      # trigger event: <TriggerEvent patchset-created openstack/neutron-specs master 128613,7
      if line =~ /trigger event: \<.*? .*? (.*?) (.*?) (.*),(.*)\>/
        project = $1
        branch = $2
        changenum = $3
        patchset = $4
        @changes[changenum] = { project: project, branch: branch }

      elsif line =~ /DEBUG .*? Adding build \<Build (.*?) of .*Change .*? ([0-9]+)\,([0-9]+)/
        #puts "JOB INFO line: #{line}"
        @jobs[$1] = { changenum: $2, patchset: $3 }

      elsif line =~ /INFO .*? Cancel build \<Build (.*?) /
        #puts "Job cancel: #{$1}"
        @jobs.delete($1)

      elsif line =~ /INFO .*? Build \<gear.Job .*? unique: (.*?)> complete\, result (.*)/
        job_id = $1
        result = $2

        if result == 'SUCCESS'
          #puts "FOUND A SUCCESSFUL JOB!"
          @consecutive_failures = 0
          @changes.delete(@jobs[job_id][:changenum])
        elsif result == 'FAILURE'
          #puts "FOUND A FAILURE: ++#{job_id}++ #{@jobs[job_id]}"
          #puts "  LINE: #{line}"
          @consecutive_failures += 1
          j = @jobs[job_id]

          #puts "Retrying job: (consecutive failures: #{@consecutive_failures})"

          redo_job(j[:changenum], j[:patchset])
        else
          #puts "UNKNOWN JOB STATE:"
          #puts line
          #puts "++#{job_id}++ #{result}"
          #puts "job hash: #{JOBS[job_id]}"
        end
        @jobs.delete(job_id)
      end

      # If consecutive failures is >N, pause jobs
      if @consecutive_failures > 20
        pause_jobs
      end
    end
  end
end

##
## MAIN
##

if `uname`.strip == "Darwin"
  # Test box
  path_lock = "/tmp/zuul-watch.lock"
else
  path_lock = "/var/run/zuul-watch.lock"

  log_file = "/var/log/zuul_watch.log"
  $stdout.reopen(log_file, "a")
  $stderr.reopen(log_file, "a")
end

# Only one of us gets to run
lock_file = File.open(path_lock, File::RDWR|File::CREAT, 0666)
exit 1 unless lock_file.flock(File::LOCK_EX|File::LOCK_NB)

# Now loop forever on zuul
z = ZuulWatcher.new
z.watch_loop
