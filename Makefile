# Makefile to run setup.py

clean:
	python3 setup.py clean

build:
	python3 -m build

install:
	pip3 install .

test:
	./tests_with_redis.sh

unittest:
	pytest -m unittest

devtest:
	./tests_with_redis.sh dev

integrationtest:
	./tests_with_redis.sh integrationtest
