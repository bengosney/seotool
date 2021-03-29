.PHONY := dev, pip-tools
.DEFAULT_GOAL := dev

INS=$(wildcard requirements.*.in)
REQS=$(subst in,txt,$(INS))

requirements.%.txt: requirements.%.in
	@echo "Builing $@"
	@pip-compile -q -o $@ $^

requirements.txt: setup.py
	@echo "Builing requirements.txt"
	@pip-compile -q

dev: requirements.txt $(REQS)
	@echo "Installing requirements"
	@pip-sync $^
