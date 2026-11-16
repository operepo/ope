#!/bin/bash
# ope-canvas-upgrade - step an old OPE canvas database up through the intermediate canvas releases until
# the current ope-canvas image can migrate it (canvas squashes old migrations, so it can't jump directly).
#
# Normally runs automatically: when ope-canvas-upgrade/.enabled exists, ope-canvas depends on it
# (service_completed_successfully) so it runs on every "docker compose up" - exits right away when there's
# nothing to do. By hand (ope-canvas must be STOPPED):
#   docker compose stop ope-canvas
#   docker compose run --rm ope-canvas-upgrade
#   docker compose up -d ope-canvas
#
# Env: IT_PW (postgres password), CANVAS_SECRET (canvas encryption key - must match ope-canvas),
#      CANVAS_DEFAULT_DOMAIN, SKIP_BACKUP=1 to skip the pg_dump, JOB_DRAIN_TIMEOUT (seconds, default 7200)
set -euo pipefail

# step | canvas release | ruby | CANVAS_RAILS | migration that must already be applied before this step
STEPS=(
    "1|release/2024-03-13.297|3.1|7.0|20180425185812"
    "2|release/2024-08-28.241|3.1|7.1|20231220155354"
    "3|release/2025-01-29.487|3.3|7.1|20240524142000"
    "4|release/2025-05-07.341|3.3|7.1|20240926011200"
    "5|release/2025-08-13.321|3.4|7.2|20241211152045"
    "6|release/2025-10-22.358|3.4|7.2|20250326180233"
    "7|release/2026-01-28.626|3.4|8.0|20250624000755"
)
# NOTE - steps always run IN ORDER. Don't skip ahead just because the db has a later step's required
# migration: canvas sometimes adds a back-dated migration that a later release squashes away
# (20241209133534_create_lti_assets showed up in 2025-03 and was squashed by 2025-06), so every step whose
# db/migrate has migrations the db hasn't run yet has to run.
# what the current ope-canvas image (release/2026-04-22.394) needs
FINAL_REQUIRED=20250930000003
# version of release/2026-04-22.394's db/migrate/*_validate_migration_integrity.rb - a db created by that
# release (fresh install) never records the squashed FINAL_REQUIRED migration but does have this one
FINAL_VALIDATE=20101201000096
INITIAL_MIGRATION=20101210192618

DB=canvas_production
BACKUP_DIR=/backups
LOG_DIR=/backups/logs
JOB_DRAIN_TIMEOUT=${JOB_DRAIN_TIMEOUT:-7200}
SHARED=/opt/canvas-upgrade/shared

export PGPASSWORD="${IT_PW:?IT_PW is required}"
: "${CANVAS_SECRET:?CANVAS_SECRET is required (must be the same value ope-canvas uses)}"
export RAILS_ENV=production

psql_q() { psql -v ON_ERROR_STOP=1 -U postgres -h postgresql -d "$DB" -tAc "$1"; }
has_mig() { [ "$(psql_q "select count(*) from schema_migrations where version='$1'")" = "1" ]; }
is_current() { has_mig "$FINAL_REQUIRED" || has_mig "$FINAL_VALIDATE"; }
newest_mig() { psql_q "select max(version) from schema_migrations where length(version) = 14"; }   # skip brand-hash versions
log() { echo "[$(date '+%F %T')] $*"; }

mkdir -p "$BACKUP_DIR" "$LOG_DIR" "$SHARED"

log "=== OPE canvas database upgrade ==="
until psql -U postgres -h postgresql -d postgres -tAc "select 1" >/dev/null 2>&1; do
    log "waiting for ope-postgresql..."; sleep 2
done

if [ "$(psql -U postgres -h postgresql -d postgres -tAc "select count(*) from pg_database where datname='$DB'")" != "1" ] \
   || [ "$(psql_q "select count(*) from pg_tables where tablename='schema_migrations'")" != "1" ]; then
    log "No existing canvas database - nothing to upgrade (ope-canvas will create a new one)."
    exit 0
fi
if has_mig "$FINAL_VALIDATE"; then
    log "Database was already migrated by the current ope-canvas - nothing to do. Start ope-canvas."
    exit 0
fi
last_step_no=$(( ${#STEPS[@]} ))
if [ "$(psql_q "select count(*) from pg_tables where schemaname='ope_audit' and tablename='upgrade_steps'")" = "1" ] \
   && [ "$(psql_q "select count(*) from ope_audit.upgrade_steps where step = $last_step_no")" = "1" ]; then
    log "All upgrade steps already done - nothing to do. Start ope-canvas."
    exit 0
fi
if ! has_mig "$INITIAL_MIGRATION"; then
    log "ERROR - $DB doesn't look like a canvas database (no migration $INITIAL_MIGRATION)."
    exit 1
fi
log "Newest migration in $DB: $(newest_mig)"

# Refuse to run while canvas is using the database (its job worker would run old jobs with new code)
others=$(psql_q "select count(*) from pg_stat_activity where datname='$DB' and pid <> pg_backend_pid()")
if [ "$others" != "0" ] && [ "${FORCE:-0}" != "1" ]; then
    log "ERROR - $others other connection(s) to $DB. Stop ope-canvas first (docker compose stop ope-canvas)."
    log "        (set FORCE=1 to ignore)"
    exit 1
fi

if [ ! -f /usr/src/app/tmp/db_sequence_range ]; then
    log "WARNING - /usr/src/app/tmp/db_sequence_range not found (is ../volumes/canvas/tmp mounted?)"
    log "          New tables will keep default id sequences until ope-canvas sets the range."
fi

# --- backup
if [ "${SKIP_BACKUP:-0}" != "1" ]; then
    f="$BACKUP_DIR/${DB}-before-upgrade-$(date +%Y%m%d-%H%M%S).dump"
    log "Backing up $DB to $f (set SKIP_BACKUP=1 to skip)..."
    pg_dump -U postgres -h postgresql -Fc -f "$f" "$DB"
    log "Backup done ($(du -h "$f" | cut -f1)). Restore with: pg_restore -U postgres -h postgresql -c -d $DB $f"
fi

# --- configs shared by every step
ESC_PW=$(printf '%s' "$IT_PW" | sed 's/"/\\"/g')
cat > "$SHARED/database.yml" <<EOF
production:
  adapter: postgresql
  encoding: utf8
  database: $DB
  host: postgresql
  port: 5432
  username: postgres
  password: "$ESC_PW"
  timeout: 50000
  pool: 20
  queue:
    adapter: postgresql
    encoding: utf8
    database: canvas_queue
    host: postgresql
    port: 5432
    username: postgres
    password: "$ESC_PW"
    timeout: 50000
    pool: 20
EOF
JWT_KEY=$(printf "%s" "ope-jwt-${CANVAS_SECRET}" | sha256sum | cut -c1-64)   # same derivation as ope-canvas start.sh
cat > "$SHARED/security.yml" <<EOF
production:
  encryption_key: $CANVAS_SECRET
  jwt_encryption_keys:
    - $JWT_KEY
  lti_iss: 'https://${CANVAS_DEFAULT_DOMAIN:-canvas.ed}'
EOF
cat > "$SHARED/domain.yml" <<EOF
production:
  domain: "${CANVAS_DEFAULT_DOMAIN:-canvas.ed}"
  ssl: true
EOF
cat > "$SHARED/delayed_jobs.yml" <<EOF
production:
  workers:
  - queue: canvas_queue
    workers: 1
EOF
chmod 600 "$SHARED"/*.yml

# Run the job worker for this step until no runnable jobs are left (data fixups queued by migrations
# must finish with the code that queued them - the next release may not have those job classes)
drain_jobs() {  # step
    local n=$1 wlog="$LOG_DIR/step$1-jobs.log" waited=0 idle=0 pending
    log "  draining background jobs (log: $wlog)"
    bundle exec script/delayed_job run >> "$wlog" 2>&1 &
    local wpid=$!
    while true; do
        sleep 15; waited=$((waited + 15))
        pending=$(psql_q "select count(*) from delayed_jobs where run_at <= now() and next_in_strand")
        if [ "$pending" = "0" ]; then idle=$((idle + 15)); else idle=0; fi
        [ $((waited % 60)) -eq 0 ] && log "    runnable jobs: $pending (${waited}s)"
        if [ "$idle" -ge 60 ]; then break; fi
        if ! kill -0 "$wpid" 2>/dev/null; then log "  WARNING - job worker exited early (see $wlog)"; break; fi
        if [ "$waited" -ge "$JOB_DRAIN_TIMEOUT" ]; then
            log "  WARNING - jobs still pending after ${JOB_DRAIN_TIMEOUT}s - continuing (raise JOB_DRAIN_TIMEOUT to wait longer)"
            break
        fi
    done
    kill -TERM "$wpid" 2>/dev/null || true
    wait "$wpid" 2>/dev/null || true
    # Periodic jobs this release scheduled for later would otherwise be picked up by the next release, which
    # may not have that job any more ("job ... is no longer scheduled" - e.g. Crocodoc). inst-jobs re-creates
    # the current release's periodic jobs when its worker starts, so dropping the pending ones is safe.
    log "  removed $(psql_q "with d as (delete from delayed_jobs where tag like 'periodic:%' and locked_by is null returning 1) select count(*) from d") pending periodic jobs (re-created by the next worker)"
    log "  failed jobs so far: $(psql_q "select count(*) from failed_jobs" 2>/dev/null || echo '?')"
}

run_step() {  # step release ruby rails
    local n=$1 rel=$2 rb=$3 rails=$4 d=/opt/canvas-upgrade/step$1
    log "=== Step $n: $rel (ruby $rb, rails $rails) ==="
    cd "$d"
    cp "$SHARED"/database.yml "$SHARED"/security.yml "$SHARED"/domain.yml "$SHARED"/delayed_jobs.yml config/
    export GEM_HOME=$d/.gems
    export PATH=$GEM_HOME/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
    export CANVAS_RAILS=$rails
    export BUNDLE_LOCKFILE=Gemfile.lock   # same as build_step.sh - only this step's lockfile
    local mlog="$LOG_DIR/step$n-migrate.log"
    # Plain db:migrate = every migration in version order. NOT predeploy-then-postdeploy like a normal
    # deploy: each step spans months of migrations, and running all predeploy ones first breaks ordering
    # (e.g. 2025-08 DropLtiAssetsForeignKeys [predeploy] ran before the migration that creates lti_assets).
    log "  db:migrate (log: $mlog)"
    bundle exec rake db:migrate ope_upgrade:fix_null_root_account_ids ope_upgrade:set_sequence_range >> "$mlog" 2>&1 \
        || { log "ERROR - migrations failed in step $n - see $mlog"; tail -30 "$mlog"; exit 1; }
    log "  newest migration now: $(newest_mig)"
    drain_jobs "$n"
    psql_q "insert into ope_audit.upgrade_steps(step, release) values ($n, '$rel') on conflict (step) do update set release = excluded.release, finished_at = now()" >/dev/null
}

# A step is done when the upgrader recorded it (ope_audit.upgrade_steps) or the db already has the step's
# newest real migration. (Not "every migration recorded": some migrations skip themselves on OPE - e.g.
# the pgvector ones - and are never recorded, so they'd look pending forever. Re-running a finished step
# would also run that old release's job worker against a newer database.)
step_done() {  # step
    local d=/opt/canvas-upgrade/step$1/db/migrate maxv
    if [ "$(psql_q "select count(*) from ope_audit.upgrade_steps where step = $1")" = "1" ]; then return 0; fi
    maxv=$(ls "$d" | grep -oE '^[0-9]{14}_' | tr -d _ | awk '$1 >= "20110000000000" && $1 < "30000000000000"' | sort | tail -1)
    has_mig "$maxv"
}

# progress table (ope_audit schema is OPE's own - created by ope-canvas ope:init_auditing)
psql_q "create schema if not exists ope_audit; create table if not exists ope_audit.upgrade_steps (step int primary key, release text not null, finished_at timestamptz not null default now())" >/dev/null

# --- step loop: every step in order, skipping ones with nothing pending
for s in "${STEPS[@]}"; do
    # Only a db made by the current ope-canvas release itself (fresh install) may stop early. Don't stop
    # just because FINAL_REQUIRED is present: 2025-10 already has it, but going straight from 2025-10 to
    # 2026-04 skips migrations that only step 7 (2026-01) has.
    if has_mig "$FINAL_VALIDATE"; then break; fi
    IFS='|' read -r n rel rb rails req <<< "$s"
    if step_done "$n"; then
        log "=== Step $n: $rel - already done, skipping ==="
        continue
    fi
    # Same rule as canvas' validate_migration_integrity: the squash check only applies while that step's
    # integrity-check migration hasn't been recorded. (Several releases share one integrity-check version,
    # and some squashed migrations are skipped on OPE by design - e.g. 20240926011200 only runs when the
    # pgvector extension is available - so checking $req unconditionally would be stricter than canvas.)
    vfiles=(/opt/canvas-upgrade/step$n/db/migrate/*_validate_migration_integrity.rb)   # glob, no pipe (pipefail + grep -m1 = SIGPIPE)
    vver=$(basename "${vfiles[0]}"); vver=${vver%%_*}
    if ! has_mig "$vver" && ! has_mig "$req"; then
        log "ERROR - step $n ($rel) needs migration $req, which the database doesn't have. Newest: $(newest_mig)"
        log "        The database is older than this upgrader supports."
        exit 1
    fi
    run_step "$n" "$rel" "$rb" "$rails"
done

if ! is_current; then
    log "ERROR - ran every step but the database still doesn't have $FINAL_REQUIRED. Newest: $(newest_mig)"
    exit 1
fi
log "=== Upgrade complete - database is ready for the current ope-canvas (newest: $(newest_mig)) ==="
log "Start ope-canvas now - it runs the remaining migrations and the OPE startup tasks."
