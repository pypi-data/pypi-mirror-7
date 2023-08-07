
FILES=fibonacci_heap_mod.py test-fibonacci-heap-mod

go:
	./this-pylint --which-2 /usr/local/cpython-2.6/bin/pylint --to-pylint $(FILES)
	pep8 --max-line-len=132 $(FILES)
	/usr/local/cpython-3.4/bin/python ./test-fibonacci-heap-mod
	/usr/local/cpython-3.0/bin/python ./test-fibonacci-heap-mod
	/usr/local/cpython-2.7/bin/python ./test-fibonacci-heap-mod
	/usr/local/cpython-2.6/bin/python ./test-fibonacci-heap-mod
	/usr/local/pypy-2.3.1/bin/pypy ./test-fibonacci-heap-mod
	/usr/local/pypy3-2.3.1/bin/pypy ./test-fibonacci-heap-mod
	/usr/local/jython-2.7b3/jython ./test-fibonacci-heap-mod

register:
	python setup.py register

publish:
	python setup.py sdist upload

clean:
	rm -f *.pyc *.class
	rm -rf __pycache__ build dist fibonacci_heap_mod.egg-info
