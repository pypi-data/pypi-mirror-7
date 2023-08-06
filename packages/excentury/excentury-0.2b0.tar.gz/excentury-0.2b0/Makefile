# excentury makefile

all: install-user

export:
	git archive --format zip --output excentury.zip master

install:
	python3 setup.py install

install-user:
	python3 setup.py install --user

build:
	python3 setup.py sdist

develop:
	python3 setup.py develop --user

clean:
	rm -rf excentury.egg-info
	rm -rf build

pypi:
	python3 setup.py sdist upload
