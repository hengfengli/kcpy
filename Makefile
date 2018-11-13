PYTHON ?= python
GIT ?= git
BUMPVERSION ?= bumpversion

bump:
	$(BUMPVERSION) patch

bump-minor:
	$(BUMPVERSION) minor

bump-major:
	$(BUMPVERSION) major

clean: clean-pyc clean-build

clean-dist: clean clean-git-force

clean-build:
	rm -rf build/ dist/ .eggs/ *.egg-info/ .tox/ .coverage cover/

clean-pyc:
	-find . -type f -a \( -name "*.pyc" -o -name "*$$py.class" \) | xargs rm
	-find . -type d -name "__pycache__" | xargs rm -r

clean-git:
	$(GIT) clean -xdn

clean-git-force:
	$(GIT) clean -xdf

test:
	pytest tests/tests.py

build:
	$(PYTHON) setup.py sdist bdist_wheel

dist: clean-dist build

publish: dist
	sh publish.sh

lint:
	flake8