# Also needs to be updated in galaxy.yml
VERSION = 0.1.0

TEST_ARGS ?= ""
PYTHON_VERSION ?= `python -c 'import platform; print("{0}.{1}".format(platform.python_version_tuple()[0], platform.python_version_tuple()[1]))'`

clean:
	rm -f community-cidre-${VERSION}.tar.gz
	rm -rf ansible_collections
	rm -rf tests/output

build: clean
	ansible-galaxy collection build

release: build
	ansible-galaxy collection publish community-cidre-${VERSION}.tar.gz

install: build
	ansible-galaxy collection install -p ansible_collections community-cidre-${VERSION}.tar.gz

test-sanity:
	ansible-test sanity --docker -v --color --python $(PYTHON_VERSION) $(?TEST_ARGS)

test-unit:
	ansible-test units --docker -v --color --python $(PYTHON_VERSION)

test-integration:
	ansible-test integration --docker -v --color --retry-on-error --python $(PYTHON_VERSION) --continue-on-error --diff --coverage $(?TEST_ARGS)

test-molecule:
	molecule test

local/test-integration:
	mkdir -p /tmp/ebuildy/cidre/t
	rm -r /tmp/ebuildy/cidre/*
	cp -r plugins roles tests utils Makefile /tmp/ebuildy/cidre/
	ansible-test integration --no-temp-workdir --color --retry-on-error --python $(PYTHON_VERSION) --continue-on-error --diff $(?TEST_ARGS)

local/test-units:
	mkdir -p /tmp/ansible_collections/ebuildy/cidre
	rm -r /tmp/ansible_collections/ebuildy/cidre/*
	cp -r plugins tests utils Makefile /tmp/ansible_collections/ebuildy/cidre/
	cd /tmp/ansible_collections/ebuildy/cidre && \
	ansible-test units --python 3.8 -v --color


downstream-test-sanity:
	./utils/downstream.sh -s

downstream-test-integration:
	./utils/downstream.sh -i

downstream-test-molecule:
	./utils/downstream.sh -m

downstream-build:
	./utils/downstream.sh -b

downstream-release:
	./utils/downstream.sh -r
