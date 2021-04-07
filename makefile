.PHONY := install, install-dev, help, tools
.DEFAULT_GOAL := install-dev

INS=$(wildcard requirements.*.in)
REQS=$(subst in,txt,$(INS))

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

requirements.%.txt: requirements.%.in
	@echo "Builing $@"
	@pip-compile -q -o $@ $^

requirements.txt: setup.py
	@echo "Builing $@"
	@pip-compile -q $^
	@sed -i 's/pip-compile $^/pip-compile/g' $@

install: requirements.txt ## Install production requirements
	@pip -q install pip-tools
	@echo "Installing $^"
	@pip-sync $^

install-dev: requirements.txt $(REQS) ## Install development requirements (default)
	@pip -q install pip-tools
	@echo "Installing $^"
	@pip-sync $^
