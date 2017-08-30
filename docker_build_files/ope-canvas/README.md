
Open Prison Education - Canvas Server


Tech Notes - 
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
	


