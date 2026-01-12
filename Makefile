test:
	PYTHONPATH='.' pytest -s

build:
	python3 -m build

install:
	python3 setup.py install

deps:
	pip3 install setuptools wheel twine build
	python3 setup.py install
	pip3 install -U -r requirements.txt
	pip3 install pytest black flake8

distcheck:
	twine check dist/*

dist:
	twine upload dist/*

lint:
	flake8 ksmyvoteinfo/*py
	black ksmyvoteinfo/*py

clean:
	rm -rf dist build *.egg-info

.PHONY: test build deps distcheck dist
