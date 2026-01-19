.PHONY: help
help:  ## Print this message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-24s\033[0m %s\n", $$1, $$2}'

.PHONY: test
test:  ## Run test suite
	PYTHONPATH='.' pytest -s

.PHONY: build
build: ## Build lib
	python3 -m build

.PHONY: install
install: ## Install lib
	pip install .

.PHONY: deps
deps: ## Install dependencies
	pip3 install setuptools wheel twine==6.0.0 build
	python3 setup.py install
	pip3 install -U -r requirements.txt
	pip3 install pytest black flake8

.PHONY: distcheck
distcheck: ## Check distribution prep
	twine check dist/*

.PHONY: dist
dist: ## Upload distribution
	twine upload dist/*

.PHONY: lint
lint: ## Run code linters
	flake8 ksmyvoteinfo/*py
	black ksmyvoteinfo/*py

.PHONY: clean
clean: ## Clean up workspace
	rm -rf src dist build *.egg-info

