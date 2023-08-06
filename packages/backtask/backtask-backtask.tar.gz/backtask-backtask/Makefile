#!/usr/bin/make -f
#
# Copyright (c) 2013,2014 Russell Stuart.
# Licensed under GPLv2, or any later version.

DESTDIR ?= /

.PHONY:	all
all:	backtask-py

.PHONY:	backtask-py
backtask-py:

.PHONY:	test
test:	
	mkdir -p coverage
	python-coverage run --parallel-mode backtask.py
	python-coverage combine
	rm -f coverage/*
	python-coverage html -d coverage
	@python-coverage report --include backtask.py | grep --silent ' 100%$$' || { echo -n "Test coverage is not 100%: "; python-coverage report --show-missing --include backtask.py | grep '[0-9]\+% '; exit 1; }

.PHONY:	clean
clean:
	rm -rf coverage .coverage *.py[co]
	rm -rf build dist MANIFEST .*.sw?

.PHONY:	install
install: install-backtask-py

.PHONY:	install-backtask-py
install-backtask-py:
	python setup.py install $(DIST_PYFLAGS) --root=$(DESTDIR)

.PHONY: pypi
pypi:
	$(MAKE) clean
	python setup.py register sdist upload --sign --identity=0xE7843A8C

RELEASE_SOURCES = \
	agpl-3.0.txt \
	backtask.py \
	backtask-py.html \
	ChangeLog.txt \
	Makefile \
	Makefile.release \
	MANIFEST.in \
	README.txt \
	setup.py

include Makefile.release

release-project-clean:: clean
