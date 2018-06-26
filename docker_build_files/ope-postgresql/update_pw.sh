#!/bin/bash

sql="ALTER USER postgres WITH PASSWORD '$IT_PW'"
echo "Updating pw..."
echo $sql
psql -U postgres --command $sql 
