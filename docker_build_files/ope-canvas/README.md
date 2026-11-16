## Overview
Open Prison Education - Canvas Server
Provides basic functionality to students and teachers to explore courses and learn basic Canvas LMS features. 
LMS is set up to run offline and integrate with OPE project.


## Canvas version / upgrading existing servers
The image builds `CANVAS_RELEASE` (see Dockerfile) - currently `release/2026-04-22.394`, the tree that was on
the canvas-lms `prod` branch when the public GitHub mirror stopped updating (2026-04-30).

Canvas squashes old database migrations. Each release only migrates a database that already has its
"last squashed" migration (`db/migrate/*_validate_migration_integrity.rb`), so a database from an older OPE
image has to step through intermediate releases. start.sh checks this and stops with a message (without
touching the database) if the database is too old.

Upgrade chain from the previous OPE image (release/2022-07-06.145):

| Step | Canvas release          | Needs migration (already applied) | Ruby / Rails |
|------|-------------------------|-----------------------------------|--------------|
| 0    | release/2022-07-06.145  | (previous OPE image)              | 2.7 / 6.1    |
| 1    | release/2024-03-13.297  | 20180425185812                    | 3.1 / 7.0    |
| 2    | release/2024-08-28.241  | 20231220155354                    | 3.1 / 7.1    |
| 3    | release/2025-01-29.487  | 20240524142000                    | 3.3 / 7.1    |
| 4    | release/2025-05-07.341  | 20240926011200                    | 3.3 / 7.1    |
| 5    | release/2025-08-13.321  | 20241211152045                    | 3.4 / 7.2    |
| 6    | release/2025-10-22.358  | 20250326180233                    | 3.4 / 7.2    |
| 7    | release/2026-01-28.626  | 20250624000755                    | 3.4 / 8.0    |
| 8    | release/2026-04-22.394  | 20250930000003                    | 3.4 / 8.0    |

The chain was checked against the migration list of every release in between, not just the squash points:
canvas sometimes adds a back-dated migration and squashes it a few releases later (e.g.
`20241209133534_create_lti_assets` first appeared in 2025-03 and was squashed by 2025-06), so jumping
straight from 2025-01 to 2025-08 would skip it. Steps always run in order.

Steps 1-7 are packaged in the separate `ope-canvas-upgrade` image (ruby code + gems for each release, no
assets). It backs up the database (pg_dump to `volumes/canvas-upgrade/`), then for each step runs
`db:migrate` and the background job queue until the data fixup jobs are done, keeping new tables' id
sequences in the server's OPE range. Fresh installs never need it.

**Optional part of the stack.** When `docker_build_files/ope-canvas-upgrade/.enabled` exists,
`rebuild_compose.py` adds it to the compose file and makes ope-canvas depend on it
(`condition: service_completed_successfully` - the `# IF_ENABLED: ope-canvas-upgrade` lines in
ope-canvas' `docker-compose-include.yml`). It then runs on every `docker compose up`:

- nothing to do (new install, or db already upgraded) - exits in a few seconds, canvas starts
- old database - backs up, runs the steps, then canvas starts (canvas stays down meanwhile; `up` waits)
- upgrade fails - ope-canvas is not started; see `volumes/canvas-upgrade/logs/`

Servers that don't need it (new installs, already upgraded): leave `.enabled` out, rebuild the compose
file, and the upgrade image doesn't have to be on the server at all. To run it by hand instead:

    docker compose stop ope-canvas
    docker compose run --rm ope-canvas-upgrade
    docker compose up -d ope-canvas      # normal ope-canvas startup migrates the rest

## Tech Notes
SHARDING CHANGES
The gem for switchman (/opt/canvas/.gems/gems/switchman-1.8.0/app/models/switchman/shard_internal.rb) sets
10 trillion to seperate shard ids and local ids. We move this 10_000_000_000_000 ==> 1_000_000_000_000_000_000

We push shard ids to the last digit in a 64bit int. We use the next 7 digits for our facility id.

Max Value -		9_223_372_036_854_775_807  ( 64 bit integer max possible value )
Shard Range - 	*_000_000_000_000_000_000  (normally set at 10trillion, but that interfered
											with our range so we bump it up, this still
											allows for 10 shards)
School Range - 	0_***_***_*00_000_000_000 ( this gives 99 billion ids for each table and
											9,999,999 facilities )
Local ID Range -0_000_000_0**_***_***_*** ( Leaves 99 billion for local ids )

FACILITY ID

Generate a facility ID based on the current minute. We then subtract 12/1/16 from it so that is
the start of our range. This should give us about 19.5 years before the range rolls over. The code
will roll over automatically at that time.

These ids are generated when a new canvas server boots the FIRST time
 (saved in volumes/canvas/tmp/db_sequence_range). Delete this file and restart the canvas server to generate
 a new range.

Conflict Danger - If you start up 2 canvas servers at the exact same minute they could potentially end up
with the same facility ID. Otherwise the odds of 2 servers ending up with the same ID are miniscule.

 
EFFECTS ON SHARD DATABASES
Unknown - You should be able to have 9 or 10 shard servers with these changes in place. In the prison
environment we have less issue with student volume and more issues with connectivity - hence the
changes to allow for offline sync capabilities.





SCRATCH PAD



CREATE TABLE IF NOT EXISTS ope_audit.import_actions (
    event_id bigserial primary key,
    schema_name text not null,
    table_name text not null,
    relid oid not null,
    session_user_name text,
    action_tstamp_tx TIMESTAMP WITH TIME ZONE NOT NULL,
    action_tstamp_stm TIMESTAMP WITH TIME ZONE NOT NULL,
    action_tstamp_clk TIMESTAMP WITH TIME ZONE NOT NULL,
    transaction_id bigint,
    application_name text,
    client_addr inet,
    client_port integer,
    client_query text,
    action TEXT NOT NULL CHECK (action IN ('I','D','U', 'T')),
    row_data jsonb,
    changed_fields jsonb,
    statement_only boolean not null,
    
    processed boolean NOT NULL default false,
    processed_on TIMESTAMP WITH TIME ZONE,
    server_id bigint not null default 0,
    sql_statement_run text not null default ''::text
);

REVOKE ALL ON ope_audit.import_actions FROM public;
ALTER TABLE ope_audit.import_actions
    OWNER to postgres;

COMMENT ON TABLE ope_audit.import_actions IS 'Impoted actions from remote servers';
CREATE INDEX IF NOT EXISTS import_actions_relid_idx ON ope_audit.import_actions(relid);
CREATE INDEX IF NOT EXISTS import_actions_action_tstamp_tx_stm_idx ON ope_audit.import_actions(action_tstamp_stm);
CREATE INDEX IF NOT EXISTS import_actions_action_idx ON ope_audit.import_actions(action);
CREATE INDEX IF NOT EXISTS import_actions_table_name_idx ON ope_audit.import_actions(table_name);
CREATE INDEX IF NOT EXISTS import_actions_processed_idx ON ope_audit.import_actions(processed);

CREATE TABLE IF NOT EXISTS ope_audit.export_log
(
    id bigint NOT NULL,
    start_id bigint NOT NULL,
    end_id bigint NOT NULL,
    export_time timestamp with time zone NOT NULL,
    server_id bigint NOT NULL,
    CONSTRAINT "Exports_pkey" PRIMARY KEY (id)
);

REVOKE ALL ON ope_audit.export_log FROM public;
ALTER TABLE ope_audit.export_log
    OWNER to postgres;
COMMENT ON TABLE ope_audit.export_log
    IS 'Keep track of exports';
	

CREATE TABLE IF NOT EXISTS ope_audit.import_log
(
    id bigint NOT NULL,
    server_id bigint NOT NULL,
    export_id bigint NOT NULL,
    imported_on timestamp with time zone,
    CONSTRAINT import_pkey PRIMARY KEY (id)
);

REVOKE ALL ON ope_audit.import_log FROM public;
ALTER TABLE ope_audit.import_log
    OWNER to postgres;
COMMENT ON TABLE ope_audit.import_log
    IS 'Keep track of imported log files';
	


