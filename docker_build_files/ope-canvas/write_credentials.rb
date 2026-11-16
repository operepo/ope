# frozen_string_literal: true

# OPE: newer canvas reads the shared service secrets (used to sign/encrypt tokens for the RCE, mathman
# requests, etc.) from Rails credentials (CanvasSecurity.services_signing_secret / services_encryption_secret)
# instead of config/dynamic_settings.yml. OPE has no Vault, so start.sh runs this on every boot to write
# Rails' standard per-environment encrypted credentials file from the existing env values:
#   config/credentials/production.yml.enc + config/credentials/production.key
# (same CANVAS_ENC_SECRET / CANVAS_SIGN_SECRET the canvas-rce container uses)
require "active_support"
require "active_support/encrypted_configuration"
require "fileutils"
require "yaml"

env = ENV.fetch("RAILS_ENV", "production")
enc = ENV["CANVAS_ENC_SECRET"].to_s
sign = ENV["CANVAS_SIGN_SECRET"].to_s
if enc.empty? || sign.empty?
  warn "=== WARNING - CANVAS_ENC_SECRET / CANVAS_SIGN_SECRET not set - RCE tokens and mathman signing won't work ==="
  exit 0
end

dir = File.join(__dir__, "config", "credentials")
dir = "/usr/src/app/config/credentials" unless File.directory?(File.join(__dir__, "config"))
FileUtils.mkdir_p(dir)
key_path = File.join(dir, "#{env}.key")
enc_path = File.join(dir, "#{env}.yml.enc")

# New key each boot is fine - the file is rewritten from env every time
File.write(key_path, ActiveSupport::EncryptedConfiguration.generate_key)
File.chmod(0o600, key_path)

secrets = {
  "canvas_security" => {
    "encryption_secret" => enc,
    "signing_secret" => sign,
  },
}
ActiveSupport::EncryptedConfiguration.new(
  config_path: enc_path,
  key_path:,
  env_key: "RAILS_MASTER_KEY",
  raise_if_missing_key: true
).write(secrets.to_yaml)
File.chmod(0o600, enc_path)
puts "=== Wrote #{enc_path} (canvas_security service secrets) ==="
