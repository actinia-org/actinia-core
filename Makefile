# Makefile to run setup.py

clean:
	python3 setup.py clean

docs:
	python3 setup.py docs

build:
	python3 setup.py build

install:
	python3 setup.py install

bdist:
	python3 setup.py bdist

dist:
	python3 setup.py dist

test:
	./tests_with_redis.sh

unittest:
	python3 setup.py test --addopts "-m unittest"

devtest:
	./tests_with_redis.sh dev

integrationtest:
	./tests_with_redis.sh integrationtest
