PYTHON=python3
PIP=pip3

build: pip.lock
	$(PYTHON) -c "import vai_chover_bot"

install: pip.lock
	$(PIP) install .

pip.lock: requirements.txt
	$(PIP) install -r requirements.txt
	touch pip.lock

run: build
	$(PYTHON) run.py

test:
	nosetests tests
