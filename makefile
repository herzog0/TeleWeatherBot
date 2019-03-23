PYTHON := python3
PIP    := pip3
LIB    := vai_chover_bot

#########################
# arquivos e diretórios #
LIB_DIR   := $(LIB)
LIB_FILES := $(shell ls $(LIB_DIR)/*.py $(LIB_DIR)/*/*.py)

TEST_DIR   := tests
TEST_FILES := $(shell ls $(TEST_DIR)/*.py)

#######################################
# simplificando as chaves de controle #
LIBRARY      := .lib.lock
REQUIREMENTS := .pip.lock
TESTS        := .tests.lock


###################
# funções básicas #
.PHONY: build
build: $(LIBRARY)

.PHONY: install
install: $(LIBRARY)
	@$(PIP) install .

.PHONY: run
run: build
	@$(PYTHON) -m $(LIB)

.PHONY: test test
test: tests
tests: $(TESTS)

######################
# chaves de controle #
$(REQUIREMENTS): requirements.txt
	@$(PIP) install -r $<
	@touch $@

$(LIBRARY): $(REQUIREMENTS) $(LIB_FILES)
	@echo Building lib...
	@$(PYTHON) -c "import $(LIB_DIR)"
	@touch $@

$(TESTS): $(LIBRARY) $(TEST_FILES)
	@nosetests $(TEST_DIR)
	@touch $@
