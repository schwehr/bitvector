# GNU -*- makefile -*-

VERSION := ${shell grep '^__version__' BitVector/__init__.py | cut -d\' -f 2}

default:
	@echo
	@echo "  *** Welcome to BitVector ${VERSION} ***"
	@echo
	@echo "  docs   -  Build documentation (html)"
	@echo
	@echo "  clean  -  Remove temporary files"
	@echo "  test   -  Run the unittests"
	@echo "  check  -  Look for rough spots"
	@echo "  sdist  -  Build a source distribution tar ball"

docs:
	pydoc -w BitVector

clean:
	rm -f *.pyc *~
	rm -f */*.pyc
	rm -rf */__pycache__
	rm -rf BitVector.egg-info

real-clean: clean
	rm -f MANIFEST  *.html
	rm -rf build dist

.PHONY: test
test:
	@echo
	@echo Testing...
	@echo
	python2 setup.py test
	python3 setup.py test

sdist: test
	@echo Building a source distribution...
	./setup.py sdist --formats=gztar,bztar

check:
	@grep -n 'TODO|FIX' */*.py *.py *.in PKG-INFO Makefile | grep -v grep
	pylint BitVector/__init__.py
	pychecker BitVector/__init__.py

clean-whitespace:
	perl -pi -e 's|\s+$$|\n|g' *.py */*.py

bdist:
	./setup.py bdist --formats=bztar

install:
	./setup.py install --root ${INSTALL_DIR}
