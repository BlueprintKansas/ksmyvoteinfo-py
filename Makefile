help: ## view this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-24s\033[0m %s\n", $$1, $$2}'

test: ## run unit tests
	PYTHONPATH='.' pytest -s

build: ## build
	python3 setup.py build

install: ## install
	python3 setup.py install

deps: ## install dependencies
	python3 setup.py install
	pip3 install -U -r requirements.txt
	pip3 install pytest black flake8

distcheck: ## prep for release
	python3 setup.py sdist

dist: ## build a release
	python3 setup.py sdist upload

lint: ## run linting tools
	flake8 ksmyvoteinfo/*py
	black ksmyvoteinfo/*py

.PHONY: test build deps distcheck dist help
