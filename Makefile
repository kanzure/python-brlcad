install:
	python setup.py install

clean:
	rm -fr build/
	rm -fr dist/
	rm -fr ctypesgen-0.0.1-py2.7.egg/
	rm -fr thing_postinstall.egg-info/
	pip uninstall -y ctypesgen
