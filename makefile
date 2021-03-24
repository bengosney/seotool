.PHONY := dev, pip-tools
.DEFAULT_GOAL := dev

%-requirements.txt: requirements.%.in
	@echo "Builing $@"
	@pip-compile -q -o $@ $^

requirements.txt: setup.py
	@echo "Builing requirements.txt"
	@pip-compile -q

dev: requirements.txt dev-requirements.txt
	@echo "Installing requirements"
	@pip-sync $^
