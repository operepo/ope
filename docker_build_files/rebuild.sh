#!/bin/sh

# Detect python path (py2 or py3 in the system)

PY3=`which python3`
PY2=`which python`

PY=$PY3

if [ -z "$PY" ]; then
  echo Switching to py2
  PY=$PY2
fi;

echo "Using Python: $PY"

$PY ../build_tools/rebuild_compose.py
