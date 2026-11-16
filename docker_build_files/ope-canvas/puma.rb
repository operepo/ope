# frozen_string_literal: true

# OPE: canvas runs under puma (supervisord -> rails server). Upstream only sets threads 0,1 because
# Instructure runs passenger; OPE needs real concurrency in the single container.
threads 6, 6
workers 3

# Upstream turns preloading off in production (forking after canvas/switchman boot isn't safe)
preload_app! false
worker_boot_timeout 240 # seconds
