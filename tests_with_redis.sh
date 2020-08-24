/src/actinia_core # cat ./script.sh
#!/usr/bin/env sh
redis-server &
sleep 1
redis-cli ping
echo $ACTINIA_CUSTOM_TEST_CFG
echo $DEFAULT_CONFIG_PATH
python3 setup.py test
