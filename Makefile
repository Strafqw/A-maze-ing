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
MAIN    := a_maze_ing.py
CONFIG  ?= config.txt

.PHONY: install run debug lint lint-strict build clean

install:
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install flake8 mypy build

run:
	$(PYTHON) $(MAIN) $(CONFIG)

debug:
	$(PYTHON) -m pdb $(MAIN) $(CONFIG)

lint:
	flake8 .
	mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports \
		--disallow-untyped-defs --check-untyped-defs

lint-strict:
	flake8 .
	mypy . --strict

build:
	$(PYTHON) -m build

clean:
	rm -rf __pycache__ */__pycache__ .mypy_cache .pytest_cache
	rm -rf build dist *.egg-info
	find . -type f -name '*.pyc' -delete
	find . -type f -name '*.pyo' -delete
