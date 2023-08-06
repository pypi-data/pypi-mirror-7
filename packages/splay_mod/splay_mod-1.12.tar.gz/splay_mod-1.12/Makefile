
go: splay_mod.py
	./this-pylint --ignore-message '.*Trailing whitespace.*' --to-pylint test-splay_mod splay_mod.py
	/usr/local/cpython-2.5/bin/python test-splay_mod
	/usr/local/cpython-2.7/bin/python test-splay_mod
	/usr/local/pypy-2.2/bin/pypy test-splay_mod
	/usr/local/cpython-3.0/bin/python test-splay_mod
	/usr/local/cpython-3.3/bin/python test-splay_mod
	/usr/local/jython-2.7b1/bin/jython test-splay_mod

splay_mod.py: splay_mod.m4
	if [ -f splay_mod.py ]; then chmod 644 splay_mod.py; fi
	m4 splay_mod.m4 > splay_mod.py
	chmod 444 splay_mod.py

clean:
	rm -rf __pycache__ *.pyc *.class splay_mod.py
	rm -rf splay_mod.egg-info dist

register:
	python setup.py register

publish:
	python setup.py sdist upload


