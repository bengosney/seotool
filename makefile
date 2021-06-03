.PHONY := install, install-dev, help, tools, clean, deploy-local, clean-deploy, dependabot
.DEFAULT_GOAL := install-dev

INS=$(wildcard requirements.*.in)
REQS=$(subst in,txt,$(INS))
PACKAGE_NAME:=$(shell python setup.py --fullname)

ifeq ($(strip $(shell git status --porcelain 2>/dev/null)),)
	GIT_TREE_STATE=clean
else
	GIT_TREE_STATE=dirty
endif

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

requirements.%.txt: requirements.%.in
	@echo "Builing $@"
	@pip-compile --no-emit-index-url -q -o $@ $^

requirements.txt: setup.py
	@echo "Builing $@"
	@pip-compile --no-emit-index-url -q $^
	@sed -i 's/pip-compile $^/pip-compile/g' $@

install: requirements.txt ## Install production requirements
	@pip -q install pip-tools
	@echo "Installing $^"
	@pip-sync $^

install-dev: requirements.txt $(REQS) ## Install development requirements (default)
	@pip -q install pip-tools
	@echo "Installing $^"
	@pip-sync $^

clean: ## Clean any tempory and build files
	@find . -type f -name '*.pyc' -exec rm -f {} +
	@find . -type d -name '__pycache__' -exec rm -rf {} +
	@rm -rf .mypy_cache
	@rm -rf .pytest_cache
	@rm -rf *.egg-info
	@find . -maxdepth 1 -type d -name results-* -exec rm -rf {} \;

clean-deploy: ## Clean local pypi
	@sudo rm -f ~/packages/${PACKAGE_NAME}.tar.gz
	@echo "Removed ${PACKAGE_NAME}"

deploy-local: ## Deploy to local pypi
	@python setup.py sdist upload -r local

dependabot: dependabot-update install-dev ## Merge all dependabot updates into current branch
	@pytest

dependabot-update:
	@git fetch
	@git branch --remotes | grep dependabot | xargs git merge
