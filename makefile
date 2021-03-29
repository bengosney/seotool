.PHONY := install, pip-tools
.DEFAULT_GOAL := install-dev

INS=$(wildcard requirements.*.in)
REQS=$(subst in,txt,$(INS))

requirements.%.txt: requirements.%.in
	@echo "Builing $@"
	@pip-compile -q -o $@ $^

requirements.txt: setup.py
	@echo "Builing $@"
	@pip-compile -q $^

install: requirements.txt
	@echo "Installing $^"
	@pip-sync $^

install-dev: requirements.txt $(REQS)
	@echo "Installing $^"
	@pip-sync $^
