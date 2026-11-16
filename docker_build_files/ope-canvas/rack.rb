# frozen_string_literal: true

# OPE: installed as config/initializers/ope_rack.rb - upstream config/initializers/rack.rb is left alone
# (it sets Rack::Utils.multipart_part_limit). Rack 3 removed Rack::Utils.key_space_limit and Rack::Chunked,
# so the old OPE copy of rack.rb can't be used any more.

# Bigger multipart read buffer - faster large uploads (videos / course imports)
Rack::Multipart::Parser.send(:remove_const, :BUFSIZE) if Rack::Multipart::Parser.const_defined?(:BUFSIZE, false)
Rack::Multipart::Parser.const_set(:BUFSIZE, 30_000_000)
