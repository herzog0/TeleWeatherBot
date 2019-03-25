PYTHON := python3
# PYTHON := pypy3
PIP    := $(PYTHON) -m pip
LIB    := vai_chover_bot

#########################
# arquivos e diretórios #
LIB_DIR   := $(LIB)
LIB_FILES := $(shell find $(LIB_DIR) -name "*.py")
LIB_CACHE := $(shell find $(LIB_DIR) -name __pycache__)

TEST_DIR   := tests
TEST_FILES := $(shell find $(TEST_DIR) -name "*.py")
TEST_CACHE := $(shell find $(TEST_DIR) -name __pycache__)

#######################################
# simplificando as chaves de controle #
LIBRARY      := .lib.lock
REQUIREMENTS := .pip.lock
TESTS        := .tests.lock


###################
# funções básicas #
.PHONY: all
all: $(LIBRARY)

.PHONY: build
build: clean-lib $(LIBRARY)

.PHONY: install
install: $(LIBRARY)
	@$(PIP) install --user .

.PHONY: run
run: $(LIBRARY)
	@$(PYTHON) -O -m $(LIB)

.PHONY: tests
tests: $(TESTS)


###########################
# limpando (para refazer) #
.PHONY: clean
clean: clean-lib

.PHONY: clean-all
clean-all: clean-req clean-lib clean-tests

.PHONY: clean-req
clean-req:
	@rm -f $(REQUIREMENTS)

.PHONY: clean-lib
clean-lib:
	@rm -rf $(LIBRARY) $(LIB_CACHE)

.PHONY: clean-tests
clean-tests:
	@rm -rf $(TESTS) $(TEST_CACHE)


######################
# chaves de controle #
$(REQUIREMENTS): requirements.txt
	@$(PIP) install --user -r $<
	@touch $@

$(LIBRARY): $(REQUIREMENTS) $(LIB_FILES)
	@echo Building lib...
	@$(PYTHON) -O -c "import $(LIB_DIR)"
	@touch $@

$(TESTS): $(LIBRARY) $(TEST_FILES)
	@nosetests $(TEST_DIR)
	@touch $@
