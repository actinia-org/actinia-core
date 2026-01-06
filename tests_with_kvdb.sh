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
  mv ${DEFAULT_CONFIG_PATH} ${DEFAULT_CONFIG_PATH}_tmp
  cp /etc/default/actinia_test_noauth ${DEFAULT_CONFIG_PATH}
  pytest -m 'noauth'
  mv ${DEFAULT_CONFIG_PATH}_tmp ${DEFAULT_CONFIG_PATH}
}

run_tests_worker (){
  # change config run tests and change config back
  mv ${DEFAULT_CONFIG_PATH} ${DEFAULT_CONFIG_PATH}_tmp
  cp /etc/default/actinia_test_worker_usedby_api ${DEFAULT_CONFIG_PATH}
  echo "Starting worker..."
  # TODO: make sure the worker is not overwriting config path from env var
  actinia-worker job_queue_0 -c /etc/default/actinia_test_worker_usedby_worker &
  WORKER_PID=$!
  echo "Running tests"
  pytest -m 'not unittest and not noauth'
  kill $WORKER_PID
  mv ${DEFAULT_CONFIG_PATH}_tmp ${DEFAULT_CONFIG_PATH}
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
