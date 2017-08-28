namespace :ope do
  desc "Deal with OPE specific startup and configuration tasks"
  
  task :enable_auditing => :environment do
	# Add the audit scheme/etc...
	ActiveRecord::Base.connection.execute( <<-SQLSTRING

CREATE SCHEMA IF NOT EXISTS ope_audit;
REVOKE ALL ON SCHEMA ope_audit FROM public;

COMMENT ON SCHEMA ope_audit IS 'Database sync code for Open Prison Education project';

CREATE OR REPLACE FUNCTION ope_audit.jsonb_minus ( arg1 jsonb, arg2 jsonb )
 RETURNS jsonb
AS $$

SELECT 
	COALESCE(json_object_agg(
        key,
        CASE
            -- if the value is an object and the value of the second argument is
            -- not null, we do a recursion
            WHEN jsonb_typeof(value) = 'object' AND arg2 -> key IS NOT NULL 
			THEN ope_audit.jsonb_minus(value, arg2 -> key)
            -- for all the other types, we just return the value
            ELSE value
        END
    ), '{}')::jsonb
FROM 
	jsonb_each(arg1)
WHERE 
	arg1 -> key <> arg2 -> key 
	OR arg2 -> key IS NULL

$$ LANGUAGE SQL;

DROP OPERATOR IF EXISTS - ( jsonb, jsonb );

CREATE OPERATOR - (
    PROCEDURE = ope_audit.jsonb_minus,
    LEFTARG   = jsonb,
    RIGHTARG  = jsonb );

SQLSTRING
	)
	
	# Run second part - split so operator can be in place when next statements run
	ActiveRecord::Base.connection.execute( <<-SQLSTRING
	
CREATE TABLE IF NOT EXISTS ope_audit.logged_actions (
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
    statement_only boolean not null
);

REVOKE ALL ON ope_audit.logged_actions FROM public;

COMMENT ON TABLE ope_audit.logged_actions IS 'History of auditable actions on audited tables, from audit.if_modified_func()';
COMMENT ON COLUMN ope_audit.logged_actions.event_id IS 'Unique identifier for each auditable event';
COMMENT ON COLUMN ope_audit.logged_actions.schema_name IS 'Database schema audited table for this event is in';
COMMENT ON COLUMN ope_audit.logged_actions.table_name IS 'Non-schema-qualified table name of table event occured in';
COMMENT ON COLUMN ope_audit.logged_actions.relid IS 'Table OID. Changes with drop/create. Get with ''tablename''::regclass';
COMMENT ON COLUMN ope_audit.logged_actions.session_user_name IS 'Login / session user whose statement caused the audited event';
COMMENT ON COLUMN ope_audit.logged_actions.action_tstamp_tx IS 'Transaction start timestamp for tx in which audited event occurred';
COMMENT ON COLUMN ope_audit.logged_actions.action_tstamp_stm IS 'Statement start timestamp for tx in which audited event occurred';
COMMENT ON COLUMN ope_audit.logged_actions.action_tstamp_clk IS 'Wall clock time at which audited event''s trigger call occurred';
COMMENT ON COLUMN ope_audit.logged_actions.transaction_id IS 'Identifier of transaction that made the change. May wrap, but unique paired with action_tstamp_tx.';
COMMENT ON COLUMN ope_audit.logged_actions.client_addr IS 'IP address of client that issued query. Null for unix domain socket.';
COMMENT ON COLUMN ope_audit.logged_actions.client_port IS 'Remote peer IP port address of client that issued query. Undefined for unix socket.';
COMMENT ON COLUMN ope_audit.logged_actions.client_query IS 'Top-level query that caused this auditable event. May be more than one statement.';
COMMENT ON COLUMN ope_audit.logged_actions.application_name IS 'Application name set when this audit event occurred. Can be changed in-session by client.';
COMMENT ON COLUMN ope_audit.logged_actions.action IS 'Action type; I = insert, D = delete, U = update, T = truncate';
COMMENT ON COLUMN ope_audit.logged_actions.row_data IS 'Record value. Null for statement-level trigger. For INSERT this is the new tuple. For DELETE and UPDATE it is the old tuple.';
COMMENT ON COLUMN ope_audit.logged_actions.changed_fields IS 'New values of fields changed by UPDATE. Null except for row-level UPDATE events.';
COMMENT ON COLUMN ope_audit.logged_actions.statement_only IS '''t'' if ope_audit event is from an FOR EACH STATEMENT trigger, ''f'' for FOR EACH ROW';

CREATE INDEX IF NOT EXISTS logged_actions_relid_idx ON ope_audit.logged_actions(relid);
CREATE INDEX IF NOT EXISTS logged_actions_action_tstamp_tx_stm_idx ON ope_audit.logged_actions(action_tstamp_stm);
CREATE INDEX IF NOT EXISTS logged_actions_action_idx ON ope_audit.logged_actions(action);
CREATE INDEX IF NOT EXISTS logged_actions_table_name_idx ON ope_audit.logged_actions(table_name);

CREATE OR REPLACE FUNCTION ope_audit.if_modified_func() RETURNS TRIGGER AS $body$
DECLARE
    ope_audit_row ope_audit.logged_actions;
    include_values boolean;
    log_diffs boolean;
    h_old jsonb;
    h_new jsonb;
    excluded_cols text[] = ARRAY[]::text[];
BEGIN
    IF TG_WHEN <> 'AFTER' THEN
        RAISE EXCEPTION 'ope_audit.if_modified_func() may only run as an AFTER trigger';
    END IF;

    ope_audit_row = ROW(
        nextval('ope_audit.logged_actions_event_id_seq'), -- event_id
        TG_TABLE_SCHEMA::text,                        -- schema_name
        TG_TABLE_NAME::text,                          -- table_name
        TG_RELID,                                     -- relation OID for much quicker searches
        session_user::text,                           -- session_user_name
        current_timestamp,                            -- action_tstamp_tx
        statement_timestamp(),                        -- action_tstamp_stm
        clock_timestamp(),                            -- action_tstamp_clk
        txid_current(),                               -- transaction ID
        current_setting('application_name'),          -- client application
        inet_client_addr(),                           -- client_addr
        inet_client_port(),                           -- client_port
        current_query(),                              -- top-level query or queries (if multistatement) from client
        substring(TG_OP,1,1),                         -- action
        NULL, NULL,                                   -- row_data, changed_fields
        'f'                                           -- statement_only
        );

    IF NOT TG_ARGV[0]::boolean IS DISTINCT FROM 'f'::boolean THEN
        ope_audit_row.client_query = NULL;
    END IF;

    IF TG_ARGV[1] IS NOT NULL THEN
        excluded_cols = TG_ARGV[1]::text[];
    END IF;

    IF (TG_OP = 'UPDATE' AND TG_LEVEL = 'ROW') THEN
        ope_audit_row.row_data = to_jsonb(OLD.*);
        ope_audit_row.changed_fields =  (to_jsonb(NEW.*) - to_jsonb(ope_audit_row.row_data)) - to_jsonb(excluded_cols);
        IF ope_audit_row.changed_fields = NULL THEN
            -- All changed fields are ignored. Skip this update.
            RETURN NULL;
        END IF;
    ELSIF (TG_OP = 'DELETE' AND TG_LEVEL = 'ROW') THEN
        ope_audit_row.row_data = to_jsonb(OLD.*) - to_jsonb(excluded_cols);
    ELSIF (TG_OP = 'INSERT' AND TG_LEVEL = 'ROW') THEN
        ope_audit_row.row_data = to_jsonb(NEW.*) - to_jsonb(excluded_cols);
    ELSIF (TG_LEVEL = 'STATEMENT' AND TG_OP IN ('INSERT','UPDATE','DELETE','TRUNCATE')) THEN
        ope_audit_row.statement_only = 't';
    ELSE
        RAISE EXCEPTION '[ope_audit.if_modified_func] - Trigger func added as trigger for unhandled case: %, %',TG_OP, TG_LEVEL;
        RETURN NULL;
    END IF;
    INSERT INTO ope_audit.logged_actions VALUES (ope_audit_row.*);
    RETURN NULL;
END;
$body$
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = pg_catalog, public;


COMMENT ON FUNCTION ope_audit.if_modified_func() IS $body$
Track changes to a table at the statement and/or row level.

Optional parameters to trigger in CREATE TRIGGER call:

param 0: boolean, whether to log the query text. Default 't'.

param 1: text[], columns to ignore in updates. Default [].

         Updates to ignored cols are omitted from changed_fields.

         Updates with only ignored cols changed are not inserted
         into the ope_audit log.

         Almost all the processing work is still done for updates
         that ignored. If you need to save the load, you need to use
         WHEN clause on the trigger instead.

         No warning or error is issued if ignored_cols contains columns
         that do not exist in the target table. This lets you specify
         a standard set of ignored columns.

There is no parameter to disable logging of values. Add this trigger as
a 'FOR EACH STATEMENT' rather than 'FOR EACH ROW' trigger if you do not
want to log row values.

Note that the user name logged is the login role for the session. The ope_audit trigger
cannot obtain the active role because it is reset by the SECURITY DEFINER invocation
of the ope_audit trigger its self.
$body$;

CREATE OR REPLACE FUNCTION ope_audit.ope_audit_table(target_table regclass, ope_audit_rows boolean, ope_audit_query_text boolean, ignored_cols text[]) RETURNS void AS $body$
DECLARE
  stm_targets text = 'INSERT OR UPDATE OR DELETE OR TRUNCATE';
  _q_txt text;
  _ignored_cols_snip text = '';
BEGIN
    EXECUTE 'DROP TRIGGER IF EXISTS ope_audit_trigger_row ON ' || target_table;
    EXECUTE 'DROP TRIGGER IF EXISTS ope_audit_trigger_stm ON ' || target_table;

    IF ope_audit_rows THEN
        IF array_length(ignored_cols,1) > 0 THEN
            _ignored_cols_snip = ', ' || quote_literal(ignored_cols);
        END IF;
        _q_txt = 'CREATE TRIGGER ope_audit_trigger_row AFTER INSERT OR UPDATE OR DELETE ON ' ||
                 target_table ||
                 ' FOR EACH ROW EXECUTE PROCEDURE ope_audit.if_modified_func(' ||
                 quote_literal(ope_audit_query_text) || _ignored_cols_snip || ');';
        RAISE NOTICE '%',_q_txt;
        EXECUTE _q_txt;
        stm_targets = 'TRUNCATE';
    ELSE
    END IF;

    _q_txt = 'CREATE TRIGGER ope_audit_trigger_stm AFTER ' || stm_targets || ' ON ' ||
             target_table ||
             ' FOR EACH STATEMENT EXECUTE PROCEDURE ope_audit.if_modified_func('||
             quote_literal(ope_audit_query_text) || ');';
    RAISE NOTICE '%',_q_txt;
    EXECUTE _q_txt;

END;
$body$
language 'plpgsql';

CREATE OR REPLACE FUNCTION ope_audit.ope_audit_table_disable(target_table regclass) RETURNS void AS $body$
DECLARE
  stm_targets text = 'INSERT OR UPDATE OR DELETE OR TRUNCATE';
  _q_txt text;
  _ignored_cols_snip text = '';
BEGIN
    EXECUTE 'DROP TRIGGER IF EXISTS ope_audit_trigger_row ON ' || target_table;
    EXECUTE 'DROP TRIGGER IF EXISTS ope_audit_trigger_stm ON ' || target_table;
END;
$body$
language 'plpgsql';

COMMENT ON FUNCTION ope_audit.ope_audit_table(regclass, boolean, boolean, text[]) IS $body$
Add auditing support to a table.

Arguments:
   target_table:     Table name, schema qualified if not on search_path
   ope_audit_rows:       Record each row change, or only audit at a statement level
   ope_audit_query_text: Record the text of the client query that triggered the audit event?
   ignored_cols:     Columns to exclude from update diffs, ignore updates that change only ignored cols.
$body$;

-- Pg doesn't allow variadic calls with 0 params, so provide a wrapper
CREATE OR REPLACE FUNCTION ope_audit.ope_audit_table(target_table regclass, ope_audit_rows boolean, ope_audit_query_text boolean) RETURNS void AS $body$
SELECT ope_audit.ope_audit_table($1, $2, $3, ARRAY[]::text[]);
$body$ LANGUAGE SQL;

-- And provide a convenience call wrapper for the simplest case
-- of row-level logging with no excluded cols and query logging enabled.
--
CREATE OR REPLACE FUNCTION ope_audit.ope_audit_table(target_table regclass) RETURNS void AS $$
SELECT ope_audit.ope_audit_table($1, BOOLEAN 't', BOOLEAN 't');
$$ LANGUAGE 'sql';

COMMENT ON FUNCTION ope_audit.ope_audit_table(regclass) IS $body$
Add ope_auditing support to the given table. Row-level changes will be logged with full client query text. No cols are ignored.
$body$;
	
	
SQLSTRING
	)
	
	# Audit all tables in the db
	ActiveRecord::Base.connection.tables.each do |table|
	  begin
		# Don't add triggers to certain tables that we don't want to merge
		# TODO - ruby way to test against an array of table names?
		if (table != "delayed_jobs" && table != "failed_jobs")
			puts "Enabling auditing on #{table}"
			ActiveRecord::Base.connection.execute("select ope_audit.ope_audit_table('#{table}');")
		else
			# Make sure to remove trigger if it exists
			puts "Disabling auditing on #{table}"
			ActiveRecord::Base.connection.execute("select ope_audit.ope_audit_table_disable('#{table}');")
		end
	  rescue
		puts "---> Error enabling auditing on #{table}"
	  end
	end
	
  end
  
  task :startup => :environment do
	# Do all startup tasks
	
	# Get the number of schema migrations so we can see if db:migrate changes anything
	pre_migrations = 0
	post_migrations = 0
	
	sql_row = ActiveRecord::Base.connection.exec_query("select count(*) as cnt from schema_migrations")
	sql_row.each do |row|
		pre_migrations = row["cnt"].to_i
	end
		
	# Make sure we are at the current table version
	#$GEM_HOME/bin/bundle exec rake db:migrate
	Rake::Task['db:migrate'].invoke
	
	# Get the number after migrations
	sql_row = ActiveRecord::Base.connection.exec_query("select count(*) as cnt from schema_migrations")
	sql_row.each do |row|
		post_migrations = row["cnt"].to_i
	end

	# Load the unique sequence range for this install to avoid ID conflicts
	#$GEM_HOME/bin/bundle exec rake ope:set_sequence_range
	Rake::Task['ope:set_sequence_range'].invoke

	# Make sure that we have loaded and enabled the audit stuff
	#$GEM_HOME/bin/bundle exec rake ope:enable_auditing
	Rake::Task['ope:enable_auditing'].invoke

	# Make sure that the assets are properly compiled (run this each time as a migrate may require a recompile)
	if (pre_migrations != post_migrations)
		puts "Migrations detected, compiling assets"
		#$GEM_HOME/bin/bundle exec rake canvas:compile_assets
		Rake::Task['canvas:compile_assets'].invoke
	else
		puts "No migrations detected"
	end
  end
  
  task :set_sequence_range => :environment do
	# If no range defined, create one and set it
	range_file = "/usr/src/app/tmp/db_sequence_range"
	rangestart = 0
	
	if File.file?(range_file) != true
		# Generate a new range and save it
		# Calculate database ID ranges based on current time.
		# Use 24675840 as the epoch time (in minutes which is about 12/1/16)
		# This allows us to start our range close to 0 and extend for about 19.5 years
		# Max - 			9_223_372_036_854_775_807
		# Shard Range - 	*_000_000_000_000_000_000  (normally set at 10trillion, but that interfered
		#												with our range so we bump it up, this still
		#												allows for 10 shards)
		# School Range - 	0_***_***_*00_000_000_000 ( this gives 99 billion ids for each table and
		#												9,999,999 facilities )
		# Local ID Range -	0_000_000_0**_***_***_*** ( Leaves 99 billion for local ids )
		rangestart = Time.now.to_i / 60 # Seconds since 1970 - convert to minutes
		rangestart = rangestart - 24675840 # Subtract 12/1/16 to start range at 0
		while rangestart > 9999999
			# If we overflow, just reset the range, odds of id conflict on the second or
			# third time through are extremely small
			rangestart = rangestart - 9999999
		end
		# Bump the range up to 100 billion (each range should have 100 billion ids)
		rangestart = rangestart * 100000000000
		
		# Store the range in a file
		begin
			File.open(range_file, 'w') do |f|
				f.puts rangestart
			end
		rescue
			puts "Error writing DB ID range to file #{range_file}"
		end
		
	else
		File.open(range_file, 'r') do |f|
			line = f.gets
			rangestart = line.to_i
		end
		puts "--> Range already defined #{rangestart}"
	end
	
	# Update the database sequences to use this range
	ActiveRecord::Base.connection.tables.each do |table|	  
	  begin
		last_seq = 0
		seq_row = ActiveRecord::Base.connection.exec_query("select nextval('#{table}_id_seq'::regclass) as nv")
		seq_row.each do |row|
			last_seq = row["nv"].to_i
		end
		#puts "-> #{table} current #{last_seq} -> #{rangestart}"
		if (last_seq < rangestart || last_seq >= rangestart + 100000000000 )
			puts "-> Last sequence outside of current range #{table} #{last_seq} -> #{rangestart}"
			ActiveRecord::Base.connection.execute("ALTER SEQUENCE #{table}_id_seq RESTART WITH #{rangestart}")
		end
	  rescue
		puts "---> Error setting sequence #{rangestart} on table #{table}"
	  end
	end
	
	# Set the logged_actions table sequence too
	last_seq = 0
	seq_row = ActiveRecord::Base.connection.exec_query("select nextval('ope_audit.logged_actions_event_id_seq'::regclass) as nv")
	seq_row.each do |row|
		last_seq = row["nv"].to_i
	end
	if (last_seq < rangestart || last_seq >= rangestart + 100000000000 )
		puts "-> Last sequence outside of current range logged_actions_event_id_seq #{last_seq} -> #{rangestart}"
		ActiveRecord::Base.connection.execute("ALTER SEQUENCE ope_audit.logged_actions_event_id_seq RESTART WITH #{rangestart}")
	end
	
	puts "--> Finished setting sequence range to #{rangestart}"
	
	# Make sure to change the constraint on the version tables so they don't blow up with big ids
	begin
		ActiveRecord::Base.connection.exec_query("alter table versions_0 drop constraint versions_0_versionable_id_check;")
	rescue
	end
	begin
		ActiveRecord::Base.connection.exec_query("alter table versions_1 drop constraint versions_1_versionable_id_check;")
	rescue
	end
  end
    
end

