#!/usr/bin/env sh
########################################################################
#
# MODULE:       tests_with_kvdb.sh
#
# AUTHOR(S):    Anika Weinmann
#               mundialis GmbH & Co. KG, Bonn
#               https://www.mundialis.de
#
# PURPOSE:      This script sets up a test environment including the kvdb (valkey) server
#
# SPDX-FileCopyrightText: (c) 2022 by mundialis GmbH & Co. KG
#
# REQUIREMENTS: sudo apt install valkey-server
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
########################################################################

run_tests_noauth (){
  # change config run tests and change config back
  mv "${DEFAULT_CONFIG_PATH}" "${DEFAULT_CONFIG_PATH}_tmp" || return 1
  cp /etc/default/actinia_test_noauth "${DEFAULT_CONFIG_PATH}" || {
    mv "${DEFAULT_CONFIG_PATH}_tmp" "${DEFAULT_CONFIG_PATH}"
    return 1
  }
  pytest -m 'noauth'
  PYTEST_RES=$?
  mv "${DEFAULT_CONFIG_PATH}_tmp" "${DEFAULT_CONFIG_PATH}" || return 1
  return "$PYTEST_RES"
}

run_tests_worker (){
  # change config run tests and change config back
  mv "${DEFAULT_CONFIG_PATH}" "${DEFAULT_CONFIG_PATH}_tmp" || return 1
  cp /etc/default/actinia_test_worker_usedby_api "${DEFAULT_CONFIG_PATH}" || {
    mv "${DEFAULT_CONFIG_PATH}_tmp" "${DEFAULT_CONFIG_PATH}"
    return 1
  }

  NUMBER_OF_WORKERS=$(python3 -c '
import configparser

config = configparser.ConfigParser()
config.read("/etc/default/actinia_test_worker_usedby_api")
print(config.getint("QUEUE", "number_of_workers"))
') || {
    mv "${DEFAULT_CONFIG_PATH}_tmp" "${DEFAULT_CONFIG_PATH}"
    return 1
  }

  if [ "$NUMBER_OF_WORKERS" -lt 1 ]; then
    echo "ERROR: number_of_workers must be greater than 0"
    mv "${DEFAULT_CONFIG_PATH}_tmp" "${DEFAULT_CONFIG_PATH}"
    return 1
  fi

  echo "Starting ${NUMBER_OF_WORKERS} workers..."

  WORKER_PIDS=""
  i=0

  # TODO: make sure the worker is not overwriting config path from env var
  while [ "$i" -lt "$NUMBER_OF_WORKERS" ]; do
    actinia-worker "job_queue_${i}" -c /etc/default/actinia_test_worker_usedby_worker &
    WORKER_PIDS="$WORKER_PIDS $!"
    i=$((i + 1))
  done

  echo "Running tests"
  pytest -m 'not unittest and not noauth'
  PYTEST_RES=$?

  for pid in $WORKER_PIDS; do
    kill "$pid"
  done

  mv "${DEFAULT_CONFIG_PATH}_tmp" "${DEFAULT_CONFIG_PATH}" || return 1
  return "$PYTEST_RES"
}

# start kvdb server
valkey-server &
sleep 1
valkey-cli ping

# start webhook server
webhook-server --host "0.0.0.0" --port "5005" &
sleep 10

# run tests
# echo "${ACTINIA_CUSTOM_TEST_CFG}"
# echo "${DEFAULT_CONFIG_PATH}"

TEST_RES=1
if [ "$1" = "dev" ]
then
  echo "Executing only 'dev' tests ..."
  pytest -m "dev"
  TEST_RES=$?
elif [ "$1" = "integrationtest" ]
then
  pytest -m 'not unittest and not noauth'
  TEST_RES=$?
  if [ ${TEST_RES} -eq 0 ]
  then
    run_tests_noauth
    TEST_RES=$?
  else
    echo "Skipping tests without authentication since other tests failed"
  fi
elif [ "$1" = "noauth" ]
then
  run_tests_noauth
  TEST_RES=$?
elif [ "$1" = "worker" ]
then
  run_tests_worker
  TEST_RES=$?
else
  pytest
  TEST_RES=$?
fi

# stop kvdb server
valkey-cli shutdown

# stop webhook server
curl http://0.0.0.0:5005/shutdown

return $TEST_RES
