install: clean
	python setup.py install

clean:
	rm -fr build/
	rm -fr dist/
	rm -fr ctypesgen-0.0.1-py2.7.egg/
	rm -fr ctypesgen_dev*.egg/
	rm -fr thing_postinstall.egg-info/
	- pip uninstall -y thing_postinstall
	- pip uninstall -y ctypesgen
	- pip uninstall -y ctypesgen-dev
	rm -fr $(VIRTUAL_ENV)/lib/python2.7/site-packages/thing_postinstall-0.0.1-py2.7.egg
	rm -fr $(VIRTUAL_ENV)/lib/python2.7/site-packages/thing_postinstall

sdist: clean
	python setup.py sdist

all: clean install
