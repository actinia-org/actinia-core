# Makefile to run setup.py

clean:
	python3 setup.py clean

build:
	python3 -m build

install:
	pip3 install .

test:
	sh ./tests_with_kvdb.sh

unittest:
	pytest -m unittest

devtest:
	sh ./tests_with_kvdb.sh dev

noauthtest:
	sh ./tests_with_kvdb.sh noauth

integrationtest:
	sh ./tests_with_kvdb.sh integrationtest

workertest:
	sh ./tests_with_kvdb.sh worker
