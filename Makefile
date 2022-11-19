.PHONY: help clean test install all init dev
.DEFAULT_GOAL := install
.PRECIOUS: requirements.%.in

HOOKS=$(.git/hooks/pre-commit)
INS=$(wildcard requirements.*.in)
REQS=$(subst in,txt,$(INS))

PYTHON_VERSION:=$(shell python --version | cut -d " " -f 2)
PIP_PATH:=.direnv/python-$(PYTHON_VERSION)/bin/pip
WHEEL_PATH:=.direnv/python-$(PYTHON_VERSION)/bin/wheel
PIP_SYNC_PATH:=.direnv/python-$(PYTHON_VERSION)/bin/pip-sync
PRE_COMMIT_PATH:=.direnv/python-$(PYTHON_VERSION)/bin/pre-commit

help: ## Display this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.gitignore:
	curl -q "https://www.toptal.com/developers/gitignore/api/visualstudiocode,python,direnv" > $@

.git: .gitignore
	git init

.pre-commit-config.yaml:
	curl https://gist.githubusercontent.com/bengosney/4b1f1ab7012380f7e9b9d1d668626143/raw/060fd68f4c7dec75e8481e5f5a4232296282779d/.pre-commit-config.yaml > $@
	python -m pip install pre-commit
	pre-commit autoupdate

$(PIP_PATH): .direnv
	@python -m ensurepip
	@python -m pip install --upgrade pip

$(WHEEL_PATH): $(PIP_PATH) .direnv
	@python -m pip install wheel

$(PIP_SYNC_PATH): $(PIP_PATH) $(WHEEL_PATH) .direnv
	@python -m pip install pip-tools

$(PRE_COMMIT_PATH): $(PIP_PATH) $(WHEEL_PATH) .direnv
	@python -m pip install pre-commit

requirements.%.in:
	echo "-c requirements.txt" > $@

requirements.%.txt: requirements.%.in requirements.txt
	@echo "Builing $@"
	@python -m piptools compile -q -o $@ $^

requirements.txt: setup.py
	@echo "Builing $@"
	@python -m piptools compile -q $^

.direnv: .envrc
	python -m pip install --upgrade pip
	python -m pip install wheel pip-tools
	@touch $@ $^

.git/hooks/pre-commit: .pre-commit-config.yaml $(PRE_COMMIT_PATH)
	python -m pip install pre-commit
	pre-commit install
	pre-commit autoupdate

.envrc:
	@echo "Setting up .envrc then stopping"
	@echo "layout python python3.10" > $@
	@touch -d '+1 minute' $@
	@false

init: .direnv .git .git/hooks/pre-commit requirements.dev.txt ## Initalise a enviroment

clean: clean-results ## Remove all build files
	find . -name '*.pyc' -delete
	find . -type d -name '__pycache__' -delete
	rm -rf .pytest_cache
	rm -f .testmondata
	rm -rf .mypy_cache
	rm -rf .hypothesis

clean-results: ## Remove any results folders
	rm -rf results-*


python: requirements.txt $(REQS)
	@echo "Installing $^"
	@python -m piptools sync $(REQS)

install: $(PIP_SYNC_PATH) python ## Install development requirements (default)

dev: init install ## Start work
	code .
