# Also needs to be updated in galaxy.yml
VERSION = $(shell cat VERSION | cut -c2-)

TEST_ARGS ?= ""
PYTHON_VERSION ?= `python -c 'import platform; print("{0}.{1}".format(platform.python_version_tuple()[0], platform.python_version_tuple()[1]))'`

TEST_FOLDER ?= .test/ansible_collections/ebuildy/cidre

clean:
	rm -f ebuildy-cidre-${VERSION}.tar.gz
	rm -rf ansible_collections
	rm -rf tests/output

build: clean
	ansible-galaxy collection build

release: build
	ansible-galaxy collection publish ebuildy-cidre-${VERSION}.tar.gz

install: build
	ansible-galaxy collection install -p ansible_collections ebuildy-cidre-${VERSION}.tar.gz

test-sanity:
	ansible-test sanity --docker -v --color --python $(PYTHON_VERSION) $(?TEST_ARGS)

test-unit:
	ansible-test units --docker -v --color --python $(PYTHON_VERSION)

test-integration:
	ansible-test integration --docker --color --retry-on-error --python $(PYTHON_VERSION) --continue-on-error --diff --coverage $(?TEST_ARGS)

test-molecule:
	molecule test

local/test-integration:
	mkdir -p /tmp/ebuildy/cidre/t
	rm -r /tmp/ebuildy/cidre/*
	cp -r plugins roles tests utils Makefile /tmp/ebuildy/cidre/
	ansible-test integration --no-temp-workdir --color --retry-on-error --python $(PYTHON_VERSION) --continue-on-error --diff $(?TEST_ARGS)

local/test-units:
	ansible-test units --python 2.7
