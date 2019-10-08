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
	make start
	python3 setup.py test
	make stop

start: server.PID

server.PID:
	{ echo "webhook-server" & echo $$! > $@; }
	sleep 3

stop: server.PID
	kill `cat $<` && rm $<

.PHONY: start stop
