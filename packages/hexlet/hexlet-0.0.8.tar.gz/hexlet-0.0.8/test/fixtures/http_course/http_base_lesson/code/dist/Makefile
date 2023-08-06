install: requirements
	mkdir -p bin
	touch bin/http_parser
	chmod u+x bin/http_parser

requirements:
	easy_install pip
	pip install -r requirements.txt

test:
	py.test

.PHONY: test
