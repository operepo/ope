# OPE tasks run by ope-canvas-upgrade between migrations of each intermediate canvas release.
# Kept separate from ope-canvas/ope.rake (that file targets the current canvas version only).
namespace :ope_upgrade do
  # Same fix ope.rake runs after db:migrate:predeploy - some predeploy migrations leave root_account_id null
  task fix_null_root_account_ids: :environment do
    puts "====== OPE_UPGRADE FIX_NULL_ROOT_ACCOUNT_IDS ======"
    Role.where(root_account_id: nil).update_all(root_account_id: 1)
    RoleOverride.where(root_account_id: nil).update_all(root_account_id: 1)
  end

  # Keep every table's id sequence inside this server's OPE school range (see ope-canvas/ope.rake
  # set_sequence_range). Migrations create new tables whose sequences start at 1 - move them into the
  # range right away so rows created by later steps / data fixup jobs get proper OPE ids.
  # Only uses an existing range - never invents a new one (ope-canvas does that on first boot).
  task set_sequence_range: :environment do
    puts "====== OPE_UPGRADE SET_SEQUENCE_RANGE ======"
    range_file = "/usr/src/app/tmp/db_sequence_range"
    local_id_range = 1_000_000_000
    school_id_range_max = 999_999

    unless File.file?(range_file)
      puts "===== WARNING - #{range_file} not found - leaving sequences alone"
      next
    end
    rangestart = File.read(range_file).to_i
    if rangestart <= 0 || rangestart > school_id_range_max
      puts "===== WARNING - invalid range #{rangestart} in #{range_file} - leaving sequences alone"
      next
    end
    rangestart_full = rangestart * local_id_range

    conn = ActiveRecord::Base.connection
    moved = []
    conn.tables.each do |table|
      seq = "#{table}_id_seq"
      next unless conn.select_value("select to_regclass('public.#{seq}') is not null")

      # peek without consuming a value
      last_value, is_called = conn.select_rows("select last_value, is_called from public.#{seq}").first
      next_val = is_called ? last_value.to_i + 1 : last_value.to_i
      if next_val < rangestart_full || next_val >= rangestart_full + local_id_range
        max_id = conn.select_value("select max(id) from public.#{conn.quote_table_name(table)}").to_i rescue 0
        restart = [rangestart_full, (max_id >= rangestart_full && max_id < rangestart_full + local_id_range) ? max_id + 1 : rangestart_full].max
        conn.execute("ALTER SEQUENCE public.#{seq} RESTART WITH #{restart}")
        moved << table
      end
    rescue => e
      puts "  #{table}: #{e.class} #{e.message.lines.first}"
    end
    puts "===== moved #{moved.size} sequences into range #{rangestart_full}: #{moved.join(", ")}" if moved.any?

    # Version partitions get a check constraint that can't hold OPE's large ids (ope.rake drops these too)
    %w[versions_0 versions_1].each do |t|
      conn.execute("alter table #{t} drop constraint if exists #{t}_versionable_id_check") if conn.table_exists?(t)
    end
  end
end
