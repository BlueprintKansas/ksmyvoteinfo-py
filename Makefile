.PHONY: help
help: ## View this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-24s\033[0m %s\n", $$1, $$2}'

test: ## Run tests
	PYTHONPATH='.' pytest -s

build: ## Build module
	python3 setup.py build

install: ## Install module
	python3 setup.py install

deps: ## Install dependencies
	python3 setup.py install
	pip3 install -U -r requirements.txt
	pip3 install pytest black flake8

distcheck: ## Pre-check distribution
	python3 setup.py sdist

dist: ## Build distribution
	python3 setup.py sdist upload

lint: ## Run code linters
	flake8 ksmyvoteinfo/*py
	black ksmyvoteinfo/*py

.PHONY: test build deps distcheck dist
