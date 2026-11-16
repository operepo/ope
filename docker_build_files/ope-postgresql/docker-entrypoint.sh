#!/usr/bin/env bash
set -Eeo pipefail
# TODO swap to -Eeuo pipefail above (after handling all potentially-unset variables)

# usage: file_env VAR [DEFAULT]
#    ie: file_env 'XYZ_DB_PASSWORD' 'example'
# (will allow for "$XYZ_DB_PASSWORD_FILE" to fill in the value of
#  "$XYZ_DB_PASSWORD" from a file, especially for Docker's secrets feature)
file_env() {
	local var="$1"
	local fileVar="${var}_FILE"
	local def="${2:-}"
	if [ "${!var:-}" ] && [ "${!fileVar:-}" ]; then
		printf >&2 'error: both %s and %s are set (but are exclusive)\n' "$var" "$fileVar"
		exit 1
	fi
	local val="$def"
	if [ "${!var:-}" ]; then
		val="${!var}"
	elif [ "${!fileVar:-}" ]; then
		val="$(< "${!fileVar}")"
	fi
	export "$var"="$val"
	unset "$fileVar"
}

# check to see if this file is being run or sourced from another script
_is_sourced() {
	# https://unix.stackexchange.com/a/215279
	[ "${#FUNCNAME[@]}" -ge 2 ] \
		&& [ "${FUNCNAME[0]}" = '_is_sourced' ] \
		&& [ "${FUNCNAME[1]}" = 'source' ]
}

# used to create initial postgres directories and if run as root, ensure ownership to the "postgres" user
docker_create_db_directories() {
	local user; user="$(id -u)"

	mkdir -p "$PGDATA"
	# ignore failure since there are cases where we can't chmod (and PostgreSQL might fail later anyhow - it's picky about permissions of this directory)
	chmod 00700 "$PGDATA" || :

	# ignore failure since it will be fine when using the image provided directory; see also https://github.com/docker-library/postgres/pull/289
	mkdir -p /var/run/postgresql || :
	chmod 03775 /var/run/postgresql || :

	# Create the transaction log directory before initdb is run so the directory is owned by the correct user
	if [ -n "${POSTGRES_INITDB_WALDIR:-}" ]; then
		mkdir -p "$POSTGRES_INITDB_WALDIR"
		if [ "$user" = '0' ]; then
			find "$POSTGRES_INITDB_WALDIR" \! -user postgres -exec chown postgres '{}' +
		fi
		chmod 700 "$POSTGRES_INITDB_WALDIR"
	fi

	# allow the container to be started with `--user`
	if [ "$user" = '0' ]; then
		find "$PGDATA" \! -user postgres -exec chown postgres '{}' +
		find /var/run/postgresql \! -user postgres -exec chown postgres '{}' +
	fi
}

# initialize empty PGDATA directory with new database via 'initdb'
# arguments to `initdb` can be passed via POSTGRES_INITDB_ARGS or as arguments to this function
# `initdb` automatically creates the "postgres", "template0", and "template1" dbnames
# this is also where the database user is created, specified by `POSTGRES_USER` env
docker_init_database_dir() {
	# "initdb" is particular about the current user existing in "/etc/passwd", so we use "nss_wrapper" to fake that if necessary
	# see https://github.com/docker-library/postgres/pull/253, https://github.com/docker-library/postgres/issues/359, https://cwrap.org/nss_wrapper.html
	local uid; uid="$(id -u)"
	if ! getent passwd "$uid" &> /dev/null; then
		# see if we can find a suitable "libnss_wrapper.so" (https://salsa.debian.org/sssd-team/nss-wrapper/-/commit/b9925a653a54e24d09d9b498a2d913729f7abb15)
		local wrapper
		for wrapper in {/usr,}/lib{/*,}/libnss_wrapper.so; do
			if [ -s "$wrapper" ]; then
				NSS_WRAPPER_PASSWD="$(mktemp)"
				NSS_WRAPPER_GROUP="$(mktemp)"
				export LD_PRELOAD="$wrapper" NSS_WRAPPER_PASSWD NSS_WRAPPER_GROUP
				local gid; gid="$(id -g)"
				printf 'postgres:x:%s:%s:PostgreSQL:%s:/bin/false\n' "$uid" "$gid" "$PGDATA" > "$NSS_WRAPPER_PASSWD"
				printf 'postgres:x:%s:\n' "$gid" > "$NSS_WRAPPER_GROUP"
				break
			fi
		done
	fi

	if [ -n "${POSTGRES_INITDB_WALDIR:-}" ]; then
		set -- --waldir "$POSTGRES_INITDB_WALDIR" "$@"
	fi

	# --pwfile refuses to handle a properly-empty file (hence the "\n"): https://github.com/docker-library/postgres/issues/1025
	eval 'initdb --username="$POSTGRES_USER" --pwfile=<(printf "%s\n" "$POSTGRES_PASSWORD") '"$POSTGRES_INITDB_ARGS"' "$@"'

	# unset/cleanup "nss_wrapper" bits
	if [[ "${LD_PRELOAD:-}" == */libnss_wrapper.so ]]; then
		rm -f "$NSS_WRAPPER_PASSWD" "$NSS_WRAPPER_GROUP"
		unset LD_PRELOAD NSS_WRAPPER_PASSWD NSS_WRAPPER_GROUP
	fi
}

# print large warning if POSTGRES_PASSWORD is long
# error if both POSTGRES_PASSWORD is empty and POSTGRES_HOST_AUTH_METHOD is not 'trust'
# print large warning if POSTGRES_HOST_AUTH_METHOD is set to 'trust'
# assumes database is not set up, ie: [ -z "$DATABASE_ALREADY_EXISTS" ]
docker_verify_minimum_env() {
	if [ -z "$POSTGRES_PASSWORD" ] && [ 'trust' != "$POSTGRES_HOST_AUTH_METHOD" ]; then
		# The - option suppresses leading tabs but *not* spaces. :)
		cat >&2 <<-'EOE'
			Error: Database is uninitialized and superuser password is not specified.
			       You must specify POSTGRES_PASSWORD to a non-empty value for the
			       superuser. For example, "-e POSTGRES_PASSWORD=password" on "docker run".

			       You may also use "POSTGRES_HOST_AUTH_METHOD=trust" to allow all
			       connections without a password. This is *not* recommended.

			       See PostgreSQL documentation about "trust":
			       https://www.postgresql.org/docs/current/auth-trust.html
		EOE
		exit 1
	fi
	if [ 'trust' = "$POSTGRES_HOST_AUTH_METHOD" ]; then
		cat >&2 <<-'EOWARN'
			********************************************************************************
			WARNING: POSTGRES_HOST_AUTH_METHOD has been set to "trust". This will allow
			         anyone with access to the Postgres port to access your database without
			         a password, even if POSTGRES_PASSWORD is set. See PostgreSQL
			         documentation about "trust":
			         https://www.postgresql.org/docs/current/auth-trust.html
			         In Docker's default configuration, this is effectively any other
			         container on the same system.

			         It is not recommended to use POSTGRES_HOST_AUTH_METHOD=trust. Replace
			         it with "-e POSTGRES_PASSWORD=password" instead to set a password in
			         "docker run".
			********************************************************************************
		EOWARN
	fi
}
# similar to the above, but errors if there are any "old" databases detected (usually due to upgrades without pg_upgrade)
docker_error_old_databases() {
	if [ -n "${OLD_DATABASES[0]:-}" ]; then
		cat >&2 <<-EOE
			Error: in 18+, these Docker images are configured to store database data in a
			       format which is compatible with "pg_ctlcluster" (specifically, using
			       major-version-specific directory names).  This better reflects how
			       PostgreSQL itself works, and how upgrades are to be performed.

			       See also https://github.com/docker-library/postgres/pull/1259

			       Counter to that, there appears to be PostgreSQL data in:
			         ${OLD_DATABASES[*]}

			       This is usually the result of upgrading the Docker image without
			       upgrading the underlying database using "pg_upgrade" (which requires both
			       versions).

			       The suggested container configuration for 18+ is to place a single mount
			       at /var/lib/postgresql which will then place PostgreSQL data in a
			       subdirectory, allowing usage of "pg_upgrade --link" without mount point
			       boundary issues.

			       See https://github.com/docker-library/postgres/issues/37 for a (long)
			       discussion around this process, and suggestions for how to do so.
		EOE
		exit 1
	fi
}

# usage: docker_process_init_files [file [file [...]]]
#    ie: docker_process_init_files /always-initdb.d/*
# process initializer files, based on file extensions and permissions
docker_process_init_files() {
	# psql here for backwards compatibility "${psql[@]}"
	psql=( docker_process_sql )

	printf '\n'
	local f
	for f; do
		case "$f" in
			*.sh)
				# https://github.com/docker-library/postgres/issues/450#issuecomment-393167936
				# https://github.com/docker-library/postgres/pull/452
				if [ -x "$f" ]; then
					printf '%s: running %s\n' "$0" "$f"
					"$f"
				else
					printf '%s: sourcing %s\n' "$0" "$f"
					. "$f"
				fi
				;;
			*.sql)     printf '%s: running %s\n' "$0" "$f"; docker_process_sql -f "$f"; printf '\n' ;;
			*.sql.gz)  printf '%s: running %s\n' "$0" "$f"; gunzip -c "$f" | docker_process_sql; printf '\n' ;;
			*.sql.xz)  printf '%s: running %s\n' "$0" "$f"; xzcat "$f" | docker_process_sql; printf '\n' ;;
			*.sql.zst) printf '%s: running %s\n' "$0" "$f"; zstd -dc "$f" | docker_process_sql; printf '\n' ;;
			*)         printf '%s: ignoring %s\n' "$0" "$f" ;;
		esac
		printf '\n'
	done
}

# Execute sql script, passed via stdin (or -f flag of pqsl)
# usage: docker_process_sql [psql-cli-args]
#    ie: docker_process_sql --dbname=mydb <<<'INSERT ...'
#    ie: docker_process_sql -f my-file.sql
#    ie: docker_process_sql <my-file.sql
docker_process_sql() {
	local query_runner=( psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --no-password --no-psqlrc )
	if [ -n "$POSTGRES_DB" ]; then
		query_runner+=( --dbname "$POSTGRES_DB" )
	fi

	PGHOST= PGHOSTADDR= "${query_runner[@]}" "$@"
}

# create initial database
# uses environment variables for input: POSTGRES_DB
docker_setup_db() {
	local dbAlreadyExists
	dbAlreadyExists="$(
		POSTGRES_DB= docker_process_sql --dbname postgres --set db="$POSTGRES_DB" --tuples-only <<-'EOSQL'
			SELECT 1 FROM pg_database WHERE datname = :'db' ;
		EOSQL
	)"
	if [ -z "$dbAlreadyExists" ]; then
		POSTGRES_DB= docker_process_sql --dbname postgres --set db="$POSTGRES_DB" <<-'EOSQL'
			CREATE DATABASE :"db" ;
		EOSQL
		printf '\n'
	fi
}

# Loads various settings that are used elsewhere in the script
# This should be called before any other functions
docker_setup_env() {
	file_env 'POSTGRES_PASSWORD'

	file_env 'POSTGRES_USER' 'postgres'
	file_env 'POSTGRES_DB' "$POSTGRES_USER"
	file_env 'POSTGRES_INITDB_ARGS'
	: "${POSTGRES_HOST_AUTH_METHOD:=}"

	declare -g DATABASE_ALREADY_EXISTS
	: "${DATABASE_ALREADY_EXISTS:=}"
	declare -ag OLD_DATABASES=()
	# look specifically for PG_VERSION, as it is expected in the DB dir
	if [ -s "$PGDATA/PG_VERSION" ]; then
		DATABASE_ALREADY_EXISTS='true'
	elif [ "$PGDATA" = "/var/lib/postgresql/$PG_MAJOR/docker" ]; then
		# https://github.com/docker-library/postgres/pull/1259
		for d in /var/lib/postgresql /var/lib/postgresql/data /var/lib/postgresql/*/docker; do
			if [ -s "$d/PG_VERSION" ]; then
				OLD_DATABASES+=( "$d" )
			fi
		done
		if [ "${#OLD_DATABASES[@]}" -eq 0 ] && [ "$PG_MAJOR" -ge 18 ] && {
			# in BusyBox, "mountpoint" only checks dev vs ino (https://github.com/tianon/mirror-busybox/blob/be7d1b7b1701d225379bc1665487ed0871b592a5/util-linux/mountpoint.c#L78) which will notably miss bind mounts entirely (which almost all Docker volume mounts are)
			# coreutils checks /proc/self/mountinfo, so we have a fallback to mimic that and directly check "/proc/self/mountinfo" to catch that case
			mountpoint -q /var/lib/postgresql/data \
			|| awk '$5 == "/var/lib/postgresql/data" { found = 1 } END { exit !found }' /proc/self/mountinfo
		}; then
			OLD_DATABASES+=( '/var/lib/postgresql/data (unused mount/volume)' )
		fi
	fi
}

# append POSTGRES_HOST_AUTH_METHOD to pg_hba.conf for "host" connections
# all arguments will be passed along as arguments to `postgres` for getting the value of 'password_encryption'
pg_setup_hba_conf() {
	# default authentication method is md5 on versions before 14
	# https://www.postgresql.org/about/news/postgresql-14-released-2318/
	if [ "$1" = 'postgres' ]; then
		shift
	fi
	local auth
	# check the default/configured encryption and use that as the auth method
	auth="$(postgres -C password_encryption "$@")"
	: "${POSTGRES_HOST_AUTH_METHOD:=$auth}"
	{
		printf '\n'
		if [ 'trust' = "$POSTGRES_HOST_AUTH_METHOD" ]; then
			printf '# warning trust is enabled for all connections\n'
			printf '# see https://www.postgresql.org/docs/17/auth-trust.html\n'
		fi
		printf 'host all all all %s\n' "$POSTGRES_HOST_AUTH_METHOD"
	} >> "$PGDATA/pg_hba.conf"
}

# start socket-only postgresql server for setting up or running scripts
# all arguments will be passed along as arguments to `postgres` (via pg_ctl)
docker_temp_server_start() {
	if [ "$1" = 'postgres' ]; then
		shift
	fi

	# internal start of server in order to allow setup using psql client
	# does not listen on external TCP/IP and waits until start finishes
	set -- "$@" -c listen_addresses='' -p "${PGPORT:-5432}"

	# unset NOTIFY_SOCKET so the temporary server doesn't prematurely notify
	# any process supervisor.
	NOTIFY_SOCKET= \
	PGUSER="${PGUSER:-$POSTGRES_USER}" \
	pg_ctl -D "$PGDATA" \
		-o "$(printf '%q ' "$@")" \
		-w start
}

# stop postgresql server after done setting up user and running scripts
docker_temp_server_stop() {
	PGUSER="${PGUSER:-postgres}" \
	pg_ctl -D "$PGDATA" -m fast -w stop
}

# check arguments for an option that would cause postgres to stop
# return true if there is one
_pg_want_help() {
	local arg
	for arg; do
		case "$arg" in
			# postgres --help | grep 'then exit'
			# leaving out -C on purpose since it always fails and is unhelpful:
			# postgres: could not access the server configuration file "/var/lib/postgresql/data/postgresql.conf": No such file or directory
			-'?'|--help|--describe-config|-V|--version)
				return 0
				;;
		esac
	done
	return 1
}

_main() {
	# if first arg looks like a flag, assume we want to run postgres server
	if [ "${1:0:1}" = '-' ]; then
		set -- postgres "$@"
	fi

	if [ "$1" = 'postgres' ] && ! _pg_want_help "$@"; then
		docker_setup_env
		# setup data directories and permissions (when run as root)
		docker_create_db_directories
		if [ "$(id -u)" = '0' ]; then
			# then restart script as postgres user
			exec gosu postgres "$BASH_SOURCE" "$@"
		fi

		# only run initialization on an empty data directory
		if [ -z "$DATABASE_ALREADY_EXISTS" ]; then
			docker_verify_minimum_env
			docker_error_old_databases

			# check dir permissions to reduce likelihood of half-initialized database
			ls /docker-entrypoint-initdb.d/ > /dev/null

			docker_init_database_dir
			pg_setup_hba_conf "$@"

			# PGPASSWORD is required for psql when authentication is required for 'local' connections via pg_hba.conf and is otherwise harmless
			# e.g. when '--auth=md5' or '--auth-local=md5' is used in POSTGRES_INITDB_ARGS
			export PGPASSWORD="${PGPASSWORD:-$POSTGRES_PASSWORD}"
			docker_temp_server_start "$@"

			docker_setup_db
			docker_process_init_files /docker-entrypoint-initdb.d/*

			docker_temp_server_stop
			unset PGPASSWORD

			cat <<-'EOM'

				PostgreSQL init process complete; ready for start up.

			EOM
		else
			cat <<-'EOM'

				PostgreSQL Database directory appears to contain a database; Skipping initialization

			EOM
		fi

		# CUSTOM CODE - OPE Project (must run before POSTGRES_* vars are unset below)
		if ! _ope_setup "$@"; then
			echo "Error doing OPE Init - something failed!"
			exit 1
		fi
		# END CUSTOM CODE

		unset "${!POSTGRES_@}"
	fi

	exec "$@"
}

# CUSTOM CODE - OPE Project
#
# Data folders live in the volume mounted at /var/lib/postgresql/data and are named by PG version:
#   pgdata        - PG 9.6  (legacy)
#   pgdata-12.9   - PG 12
#   pgdata-18     - PG 18  (current - $PG_MAJOR comes from the base image)
# When a new major version starts and finds the previous version's folder (without a CONVERTED
# marker), it pg_upgrades that data into the new folder. The old folder is left intact (copy mode).
#
# To add the next upgrade (e.g. 18 -> 22): copy the PG18 binaries into /pg18 in the Dockerfile and
# point OPE_PREV_* at pgdata-18 / /pg18.
OPE_DATA_ROOT=/var/lib/postgresql/data
OPE_PREV_PGDATA="$OPE_DATA_ROOT/pgdata-12.9"
OPE_PREV_MAJOR=12
OPE_PREV_BINDIR=/pg12/bin
OPE_PREV_LIBPATH=/pg12/icu  # extra shared libs (ICU 74) needed by the PG12 binaries on this base image
OPE_LEGACY_PGDATA="$OPE_DATA_ROOT/pgdata"  # PG 9.6 - must go through the 12.9 image first

# Start/stop a socket-only temp server on the NEW cluster
_ope_temp_start() {
	pg_ctl -D "$PGDATA" -o "-c listen_addresses=''" -w start
}
_ope_temp_stop() {
	pg_ctl -D "$PGDATA" -m fast -w stop
}

_ope_tune_config() {
	# Get the current total memory (GB)
	local TOTAL_MEM SHARED_BUFFERS WORK_MEM
	TOTAL_MEM=$(awk '/MemTotal/ {printf "%.0f \n", $2/1024/1024 }' /proc/meminfo)
	SHARED_BUFFERS="64MB"
	WORK_MEM="8MB"
	if [ "$TOTAL_MEM" -gt 3 ]; then SHARED_BUFFERS="128MB"; fi
	if [ "$TOTAL_MEM" -gt 6 ]; then SHARED_BUFFERS="256MB"; fi
	if [ "$TOTAL_MEM" -gt 10 ]; then SHARED_BUFFERS="512MB"; fi
	if [ "$TOTAL_MEM" -gt 14 ]; then SHARED_BUFFERS="728MB"; fi
	if [ "$TOTAL_MEM" -gt 22 ]; then SHARED_BUFFERS="1024MB"; fi
	if [ "$TOTAL_MEM" -gt 30 ]; then SHARED_BUFFERS="2048MB"; fi

	# Increase memory
	sed -i "s/^shared_buffers = .*/shared_buffers = $SHARED_BUFFERS/g" "$PGDATA/postgresql.conf"
	sed -i "s/#work_mem = 4MB/work_mem = $WORK_MEM/" "$PGDATA/postgresql.conf"

	# Change max connections
	echo Changing max_connections...
	sed -i "s/max_connections = 100/max_connections = 500/" "$PGDATA/postgresql.conf"
}

# Make sure the postgres password matches IT_PW. Also needed after an upgrade - pg_upgrade brings
# over the old md5 password hash, and PG14+ clusters authenticate with scram-sha-256.
_ope_reset_password() {
	_ope_temp_start || return 1
	echo Resetting OPE password...
	psql -v ON_ERROR_STOP=1 -U postgres --no-psqlrc --set pw="$POSTGRES_PASSWORD" <<-'EOSQL'
		ALTER USER postgres WITH PASSWORD :'pw' ;
	EOSQL
	local rc=$?
	_ope_temp_stop || return 1
	return $rc
}

# Upgrade the previous major version's data folder into $PGDATA if needed
_ope_upgrade_check() {
	echo "Checking upgrade status from PG $OPE_PREV_MAJOR -> PG $PG_MAJOR..."

	# A failed upgrade leaves this marker so we don't retry (and re-copy everything) on every restart
	if [ -f "$PGDATA/OPE_UPGRADE_FAILED" ]; then
		cat >&2 <<-EOE
			*****************************************************************************
			ERROR: A previous upgrade from PG $OPE_PREV_MAJOR to PG $PG_MAJOR failed.
			       See $PGDATA/OPE_UPGRADE_FAILED and the logs in
			       $PGDATA/pg_upgrade_output.d (volumes/postgresql/data/pgdata-$PG_MAJOR).
			       The old data in $OPE_PREV_PGDATA has NOT been changed.
			       To retry: fix the problem, delete the pgdata-$PG_MAJOR folder and restart.
			*****************************************************************************
		EOE
		return 1
	fi

	if [ ! -s "$OPE_PREV_PGDATA/PG_VERSION" ]; then
		# Nothing to upgrade from - make sure we aren't sitting on un-upgraded 9.6 data
		if [ -s "$OPE_LEGACY_PGDATA/PG_VERSION" ] && [ ! -f "$OPE_LEGACY_PGDATA/CONVERTED" ]; then
			cat >&2 <<-EOE
				*****************************************************************************
				ERROR: Found PG $(cat "$OPE_LEGACY_PGDATA/PG_VERSION") data in $OPE_LEGACY_PGDATA that was never upgraded.
				       This image can only upgrade from PG $OPE_PREV_MAJOR. Run the previous
				       ope-postgresql image (postgres 12.9) once to upgrade 9.6 -> 12, then
				       start this image again.
				*****************************************************************************
			EOE
			return 1
		fi
		echo "No PG $OPE_PREV_MAJOR data found - nothing to upgrade."
		return 0
	fi

	if [ -f "$OPE_PREV_PGDATA/CONVERTED" ]; then
		echo "PG $OPE_PREV_MAJOR data already converted - nothing to upgrade."
		return 0
	fi

	local old_version
	old_version="$(cat "$OPE_PREV_PGDATA/PG_VERSION")"
	if [ "$old_version" != "$OPE_PREV_MAJOR" ]; then
		echo >&2 "ERROR: $OPE_PREV_PGDATA contains PG $old_version data, expected PG $OPE_PREV_MAJOR!"
		return 1
	fi

	_ope_do_upgrade
}

_ope_do_upgrade() {
	local rc=0

	# pg_upgrade needs a writable cwd (it writes logs/scripts there)
	local OLD_PWD; OLD_PWD="$(pwd)"
	cd "$PGDATA" || return 1

	# Make sure old database was shut down cleanly - start it (runs crash recovery if needed), then stop it
	echo "Making sure PG $OPE_PREV_MAJOR data is clean..."
	if ! LD_LIBRARY_PATH="$OPE_PREV_LIBPATH" "$OPE_PREV_BINDIR/pg_ctl" -D "$OPE_PREV_PGDATA" \
			-o "-c listen_addresses='' -c jit=off" -w -t 600 start \
		|| ! LD_LIBRARY_PATH="$OPE_PREV_LIBPATH" "$OPE_PREV_BINDIR/pg_ctl" -D "$OPE_PREV_PGDATA" -m fast -w stop; then
		echo >&2 "ERROR: Unable to start/stop the PG $OPE_PREV_MAJOR database in $OPE_PREV_PGDATA - not upgrading."
		cd "$OLD_PWD"
		return 1
	fi

	echo "Upgrading postgresql $OPE_PREV_MAJOR to $PG_VERSION ($OPE_PREV_PGDATA -> $PGDATA)..."
	echo "  (copy mode - old data is left untouched; this can take a while for large databases)"
	if LD_LIBRARY_PATH="$OPE_PREV_LIBPATH" pg_upgrade \
			--old-datadir "$OPE_PREV_PGDATA" --new-datadir "$PGDATA" \
			--old-bindir "$OPE_PREV_BINDIR" --new-bindir /usr/local/bin \
			--old-options "-c jit=off" \
			--username postgres; then
		# Mark that the upgrade has happened
		echo "Upgraded to PG $PG_VERSION on $(date)" > "$OPE_PREV_PGDATA/CONVERTED"
		echo "Upgrade from PG $OPE_PREV_MAJOR to PG $PG_VERSION succeeded."

		if _ope_temp_start; then
			# If we ended up with this file, need to run it
			if [ -f "$PGDATA/update_extensions.sql" ]; then
				echo "- Running update_extensions.sql...."
				psql -U postgres --no-psqlrc --file="$PGDATA/update_extensions.sql" postgres || rc=1
			fi
			# pg_upgrade does not carry over planner statistics - rebuild them or queries will be slow
			# PG18+ pg_upgrade carries most stats over - only fill in what's missing (e.g. extended stats)
			echo "- Rebuilding missing optimizer statistics (vacuumdb --analyze-in-stages --missing-stats-only)..."
			vacuumdb -U postgres --all --analyze-in-stages --missing-stats-only || rc=1
			# ...and refresh the cumulative stats autovacuum relies on (pg_upgrade's recommendation)
			vacuumdb -U postgres --all --analyze-only || rc=1
			_ope_temp_stop || rc=1
		else
			rc=1
		fi
	else
		rc=$?
		echo "pg_upgrade exited with code $rc on $(date) - see pg_upgrade_output.d for logs" > "$PGDATA/OPE_UPGRADE_FAILED"
		echo >&2 "ERROR: Failed to upgrade PG $OPE_PREV_MAJOR to PG $PG_MAJOR! Old data in $OPE_PREV_PGDATA is untouched."
	fi

	# Move us back to the original folder we were in
	cd "$OLD_PWD"
	return $rc
}

_ope_setup() {
	_ope_tune_config || return 1
	_ope_upgrade_check || return 1
	# Reset after the upgrade so the password is stored as scram-sha-256 in the new cluster
	_ope_reset_password || return 1
	return 0
}

# Make sure we use the data folder for this major version (pgdata-18, etc...)
OPE_PGDATA="$OPE_DATA_ROOT/pgdata-$PG_MAJOR"
if [ "$PGDATA" != "$OPE_PGDATA" ]; then
	echo "Using versioned data folder: PGDATA=$OPE_PGDATA (was $PGDATA)"
	export PGDATA="$OPE_PGDATA"
fi

# PG18+ initdb enables data checksums by default, but pg_upgrade needs the new cluster to match the
# old one (PG12 clusters were created without checksums). So if this start is going to create the
# new cluster AND then upgrade into it, initdb without checksums. Fresh installs keep checksums on.
# (Checksums can be turned on later, offline, with: pg_checksums --enable -D $PGDATA)
if [ ! -s "$PGDATA/PG_VERSION" ] \
	&& [ -s "$OPE_PREV_PGDATA/PG_VERSION" ] && [ ! -f "$OPE_PREV_PGDATA/CONVERTED" ] \
	&& [[ "${POSTGRES_INITDB_ARGS:-}" != *--no-data-checksums* ]]; then
	echo "Upgrade pending from $OPE_PREV_PGDATA - new cluster will be created with --no-data-checksums"
	export POSTGRES_INITDB_ARGS="${POSTGRES_INITDB_ARGS:-} --no-data-checksums"
fi
# END CUSTOM CODE

if ! _is_sourced; then
	_main "$@"
fi

