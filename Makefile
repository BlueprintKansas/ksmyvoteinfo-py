test:
	PYTHONPATH='.' pytest -s

build:
	python3 setup.py build

install:
	python3 setup.py install

deps:
	python3 setup.py install
	pip3 install -U -r requirements.txt
	pip3 install pytest

distcheck:
	python3 setup.py sdist

dist:
	python3 setup.py sdist upload

.PHONY: test build deps distcheck dist
