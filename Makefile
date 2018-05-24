test:
	PYTHONPATH='.' pytest -s

build:
	python setup.py build

deps:
	python setup.py install
	pip install -U -r requirements.txt
	pip install pytest

.PHONY: test build
