all: clean-pyc test

test:
	python setup.py nosetests --stop --tests tests.py

travis:
	export TESTER_URL=http://$(HTTPHQ_HOST):$(HTTPHQ_PORT)/
	httphq server start --port=$(HTTPHQ_PORT) --host=$(HTTPHQ_HOST)&
	python setup.py nosetests --tests tests.py

coverage:
	python setup.py nosetests  --with-coverage --cover-package=human_curl --cover-html --cover-html-dir=coverage_out coverage


shell:
	../venv/bin/ipython

audit:
	python setup.py autdit

release: clean-pyc
	git tag -f v$(version) && git push --tags
	python setup.py sdist bdist_wininst upload

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +

find-print:
	grep -r --include=*.py --exclude-dir=venv --exclude=fabfile* --exclude=tests.py --exclude-dir=tests --exclude-dir=commands 'print' ./
