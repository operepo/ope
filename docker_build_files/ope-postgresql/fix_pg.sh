#!/bin/bash

DATADIR=$PGDATA 
# /var/lib/postgresql/data/pgdata

# Issues with invalid checkpoint record
su postgres
pg_resetxlog -f $DATADIR

# Not found?
# pg_resetwal -f $DATADIR

exit