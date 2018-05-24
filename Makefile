test:
	PYTHONPATH='.' pytest -s

build:
	python setup.py build

.PHONY: test build
