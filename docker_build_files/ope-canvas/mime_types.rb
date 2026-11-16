# frozen_string_literal: true

# OPE: installed as config/initializers/ope_mime_types.rb - upstream config/initializers/mime_types.rb is
# left alone (newer canvas registers extra LTI 1.3 types there that the old OPE copy dropped).

# Some theme/brand css links end up as /fonts/css.css2 (google fonts css2 API rewritten to local fonts)
Mime::Type.register "text/css", :css2 unless Mime::Type.lookup_by_extension(:css2)
