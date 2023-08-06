###
# distribution and building makefile for SALVE
# Used to bundle up the various setuptools operations needed to do a release
#
# NO ONE SAID THIS WOULD BE PRETTY
# JUST NEEDS TO WORK FOR ME
###

MOVING_FILES=setup.py MANIFEST.in requirements.txt

SETUP_OPTIONS=

.PHONY: copy-files clean
stablebuild: build
all: build

copy-files:
	cp ${MOVING_FILES} ../

clean:
	cd .. && rm ${MOVING_FILES}

distclean: clean
	rm -r ../.setup-venv ../dist ../build ../salve.egg-info

../.setup-venv: requirements.txt
	virtualenv ../.setup-venv
	../.setup-venv/bin/pip install -r requirements.txt

dev:
	$(MAKE) build SETUP_OPTIONS="egg_info --tag-build=.dev"

build: copy-files ../.setup-venv
	cd .. && .setup-venv/bin/python setup.py ${SETUP_OPTIONS} sdist bdist_egg
	cd .. && . .setup-venv/bin/activate; twine upload dist/*
	$(MAKE) clean
