#!/bin/bash

function cleanup() {
  exit_code=$?
  set +e
  docker rmi -f $(docker images -qf "dangling=true") &>/dev/null
  exit $exit_code
}
trap cleanup INT TERM EXIT

set -e

echo "#################################################################################################################"
echo "## MathMan - Setup "
echo "#################################################################################################################"
echo

docker-compose build --pull web

echo "#################################################################################################################"
echo "## MathMan - JS TESTS"
echo "#################################################################################################################"
echo

docker-compose run --rm web npm run test
