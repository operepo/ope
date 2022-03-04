#!/bin/bash

# If having trouble migrating and getting a PG::UniqueViolation Error  - duplicate key value violates constraint index_role_overrides_on_context_role_permission
# https://github.com/instructure/canvas-lms/issues/1806
# Then run this command to drop the index on that table, then the migration can finish.

docker-compose exec ope-postgresql bash -c "psql -U postgres -d canvas_production -c 'drop index index_role_overrides_on_context_role_permission;'"


