#threads 12,64
threads 6,6
#workers 1
workers 3
preload_app!


on_worker_boot do
  # Connect to databases when forked
  ActiveRecord::Base.establish_connection
end

