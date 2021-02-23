.PHONY: dev
.DEFAULT_GOAL: dev

%-requirements.txt: requirements.%.in
	pip-compile -o $@ $^

dev: requirements.txt dev-requirements.txt
	pip install pip-tools
	pip-sync $^
