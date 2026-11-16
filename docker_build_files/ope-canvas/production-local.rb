# frozen_string_literal: true

# OPE: loaded by upstream config/environments/production.rb (it evals config/environments/production-*.rb
# inside its Rails.application.configure block, so `config` is available here).
# Only the settings OPE changes from the upstream production.rb belong in this file.

# Cache compiled views
config.action_view.cache_template_loading = true

# Static files - the gateway serves public/ through X-Accel-Redirect (sendfile volume) but rails also
# needs to be able to serve them directly (RAILS_SERVE_STATIC_FILES / no separate web server in the container)
config.action_dispatch.x_sendfile_header = "X-Accel-Redirect"
config.public_file_server.enabled = true

# Offline install - don't fail requests if outgoing mail can't be delivered
config.action_mailer.raise_delivery_errors = false

# Upstream already sets force_ssl = true (with redirect: false - the gateway handles http -> https)

# Allow the OPE domains (rails host authorization)
config.hosts << ENV["CANVAS_DEFAULT_DOMAIN"] if ENV["CANVAS_DEFAULT_DOMAIN"]
config.hosts << ENV["VIRTUAL_HOST"] if ENV["VIRTUAL_HOST"]
ENV["ADDITIONAL_ALLOWED_HOSTS"]&.split(",")&.each do |host|
  config.hosts << host
end
