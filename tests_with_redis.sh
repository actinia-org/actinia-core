#!/usr/bin/env sh

run_tests_noauth (){
  # change config run tests and change config bag
  mv ${ACTINIA_CUSTOM_TEST_CFG} ${ACTINIA_CUSTOM_TEST_CFG}_tmp
  cp /etc/default/actinia_test_noauth ${ACTINIA_CUSTOM_TEST_CFG}
  pytest -m 'noauth'
  mv ${ACTINIA_CUSTOM_TEST_CFG}_tmp ${ACTINIA_CUSTOM_TEST_CFG}
}


# start redis server
redis-server &
sleep 1
redis-cli ping

# start webhook server
webhook-server --host "0.0.0.0" --port "5005" &
sleep 10

# run tests
echo $ACTINIA_CUSTOM_TEST_CFG
echo $DEFAULT_CONFIG_PATH

TEST_RES=1
if [ "$1" == "dev" ]
then
  echo "Executing only 'dev' tests ..."
  pytest -m 'dev'
  TEST_RES=$?
elif [ "$1" == "integrationtest" ]
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
elif [ "$1" == "noauth" ]
then
  run_tests_noauth
  TEST_RES=$?
else
  pytest
  TEST_RES=$?
fi

# stop redis server
redis-cli shutdown

# stop webhook server
curl http://0.0.0.0:5005/shutdown

return $TEST_RES
