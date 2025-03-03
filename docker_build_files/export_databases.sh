#!/bin/bash

# If having trouble migrating and getting a PG::UniqueViolation Error  - duplicate key value violates constraint index_role_overrides_on_context_role_permission
# https://github.com/instructure/canvas-lms/issues/1806
# Then run this command to drop the index on that table, then the migration can finish.


compose=`which docker-compose`

if [ -z "$compose" ]; then
  compose="docker compose"
fi;
echo "Using Compose: $compose"

# Get the current date in YYYYMMDD format
current_date=$(date +"%Y%m%d")

# Backup files older than this are removed
DAYS_TO_KEEP=${1:-30}

# Check if DAYS_TO_KEEP is numeric
if ! [[ "$DAYS_TO_KEEP" =~ ^[0-9]+$ ]]; then
  echo "Invalid input for DAYS_TO_KEEP. Defaulting to 30 days."
  DAYS_TO_KEEP=30
fi

# Calculate the cutoff date
cutoff_date=$(date -d "-${DAYS_TO_KEEP} days" +"%Y%m%d")

#$compose exec ope-postgresql bash -c "psql -U postgres -d canvas_production -c 'drop index index_role_overrides_on_context_role_permission;'"
# Dump postgresql databases - canvas_production, canvas_queue, postgres
PG_BACKUP_DIR=/var/lib/postgresql/data/backups
$compose exec ope-postgresql bash -c "mkdir -p ${PG_BACKUP_DIR}"

echo .
echo .
echo "Dumping Postgres databases..."
$compose exec ope-postgresql bash -c "pg_dump -U postgres -d canvas_production > ${PG_BACKUP_DIR}/canvas_production_${current_date}.sql"
$compose exec ope-postgresql bash -c "pg_dump -U postgres -d canvas_queue > ${PG_BACKUP_DIR}/canvas_queue_${current_date}.sql"
$compose exec ope-postgresql bash -c "pg_dump -U postgres -d postgres > ${PG_BACKUP_DIR}/postgres_${current_date}.sql"


# Dump mysql databases
# information_schema, mysql, performance_schema, fog
MYSQL_BACKUP_DIR=/var/lib/mysql/backups
$compose exec ope-fog bash -c "mkdir -p ${MYSQL_BACKUP_DIR}"

echo .
echo .
echo "Dumping MySQL databases..."
$compose exec ope-fog bash -c "mysqldump --all-databases > ${MYSQL_BACKUP_DIR}/all_database_${current_date}.sql"

# Clean up old backup files (older than DAYS_TO_KEEP days)
# Remove MySQL backup files older than DAYS_TO_KEEP
echo .
echo .
echo "Cleaning up old database backup files older than ${DAYS_TO_KEEP} days..."
#$compose exec ope-fog bash -c "find ${MYSQL_BACKUP_DIR} -type f -name '*.sql' | awk -v cutoff_date=${cutoff_date} -F'[_|.]' '{if ($NF < cutoff_date) print $0}' | xargs rm -f"
#$compose exec ope-postgresql bash -c "find ${PG_BACKUP_DIR} -type f -name '*.sql' | awk -v cutoff_date=${cutoff_date} -F'[_|.]' '{if ($NF < cutoff_date) print $0}' | xargs rm -f"
$compose exec ope-fog bash -c "find ${MYSQL_BACKUP_DIR} -type f -name '*.sql' | while read file; do
  file_date=\$(basename \$file | awk -F'[_|.]' '{print \$(NF-1)}')
  if [[ \$file_date < ${cutoff_date} ]]; then
    rm -f \$file
  fi
done"

$compose exec ope-postgresql bash -c "find ${PG_BACKUP_DIR} -type f -name '*.sql' | while read file; do
  file_date=\$(basename \$file | awk -F'[_|.]' '{print \$(NF-1)}')
  if [[ \$file_date < ${cutoff_date} ]]; then
    rm -f \$file
  fi
done"

echo .
echo .
echo "Database backups completed."