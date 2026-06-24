# A-Maze-ing — project automation
#
# Usage:
#   make install      install development tools (flake8, mypy)
#   make run          generate a maze and launch the visualizer
#   make debug        run the main script under pdb
#   make lint         run flake8 and mypy with the mandatory flags
#   make lint-strict  run flake8 and mypy --strict
#   make build        build the mazegen-* wheel and sdist into dist/
#   make clean        remove caches and temporary artifacts

PYTHON  ?= python3

PYTHON_ENV := .venv/bin/python
FLAKE8 := .venv/bin/flake8
MYPY := .venv/bin/mypy
MAIN    := a_maze_ing.py
CONFIG  ?= config.txt

.PHONY: install run debug lint lint-strict build clean

install:
	$(PYTHON) -m venv .venv
	$(PYTHON_ENV) -m pip install --upgrade pip
	$(PYTHON_ENV) -m pip install -r requirements.txt

run:
	$(PYTHON_ENV) $(MAIN) $(CONFIG)

debug:
	$(PYTHON_ENV) -m pdb $(MAIN) $(CONFIG)

lint:
	$(FLAKE8) . --exclude=.venv
	$(MYPY) . --warn-return-any --warn-unused-ignores --ignore-missing-imports \
		--disallow-untyped-defs --check-untyped-defs

lint-strict:
	$(FLAKE8) . --exclude=.venv
	$(MYPY) . --strict

build:
	$(PYTHON_ENV) -m build

clean:
	rm -rf __pycache__ */__pycache__ .mypy_cache .pytest_cache
	rm -rf build dist *.egg-info
	rm -rf .venv
	find . -type f -name '*.pyc' -delete
	find . -type f -name '*.pyo' -delete
