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
build: lib

.PHONY: install
install: requirements
	@$(PIP) install .

.PHONY: run
run: build
	@$(PYTHON) run.py

.PHONY: test test
test: tests
tests: lib tests.lock

###################
# intermediadores #
.PHONY: lib
lib: lib.lock

.PHONY: requirements
requirements: pip.lock

######################
# chaves de controle #
pip.lock: requirements.txt
	@$(PIP) install -r requirements.txt
	@touch pip.lock

lib.lock: requirements $(LIB_FILES)
	@$(PYTHON) -c "import $(LIB_DIR)"
	@touch lib.lock

tests.lock: $(TEST_FILES)
	@nosetests $(TEST_DIR)
	@touch tests.lock
