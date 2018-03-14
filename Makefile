# Makefile to run setup.py

clean:
	python setup.py clean

docs:
	python setup.py docs

build:
	python setup.py build

install:
	python setup.py install

bdist:
	python setup.py bdist

dist:
	python setup.py dist

test:
	python setup.py test
