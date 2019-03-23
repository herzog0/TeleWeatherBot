PYTHON := python3
PIP    := pip3

#########################
# arquivos e diretórios #
LIB_DIR   := $(shell basename $(shell pwd))
LIB_FILES := $(shell ls $(LIB_DIR)/*.py $(LIB_DIR)/*/*.py)

TEST_DIR   := tests
TEST_FILES := $(shell ls $(TEST_DIR)/*.py)

###################
# funções básicas #
.PHONY: build
build: .lib.lock

.PHONY: install
install: .lib.lock
	@$(PIP) install .

.PHONY: run
run: build
	@$(PYTHON) run.py

.PHONY: test test
test: tests
tests: .tests.lock

######################
# chaves de controle #
.pip.lock: requirements.txt
	@$(PIP) install -r $<
	@touch .pip.lock

.lib.lock: .pip.lock $(LIB_FILES)
	@echo Building lib...
	@$(PYTHON) -c "import $(LIB_DIR)"
	@touch .lib.lock

.tests.lock: .lib.lock $(TEST_FILES)
	@nosetests $(TEST_DIR)
	@touch .tests.lock
