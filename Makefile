test:
	PYTHONPATH='.' pytest -s

build:
	python setup.py build

deps:
	python setup.py install
	pip install -U -r requirements.txt
	pip install pytest

distcheck:
	python setup.py sdist

dist:
	python setup.py sdist upload

.PHONY: test build deps distcheck dist
