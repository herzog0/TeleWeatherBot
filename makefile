PYTHON ?= python3

PIP       := $(PYTHON) -m pip
TESTER    := $(PYTHON) -m nose
LIB       := vai_chover_bot
DOCS_TYPE := html


#########################
# arquivos e diretórios #
LIB_DIR   := $(LIB)
LIB_FILES := $(shell find $(LIB_DIR) -name "*.py" -type f)
LIB_CACHE := $(shell find $(LIB_DIR) -name __pycache__ -type d)

TEST_DIR   := tests
TEST_FILES := $(shell find $(TEST_DIR) -name "*.py" -type f)
TEST_CACHE := $(shell find $(TEST_DIR) -name __pycache__ -type d)

DOCS_DIR   := docs
DOCS_FILES := $(shell find $(DOCS_DIR) -iregex "$(DOCS_DIR)/[^_].*")

#######################################
# simplificando as chaves de controle #
LIBRARY      := .lib.lock
REQUIREMENTS := .pip.lock
DEV_REQS     := .pip.dev.lock
INSTALL      := .install.lock
TESTS        := .tests.lock
DOCS         := .docs.lock

#########################
# variáveis de ambiente #
DOTENV ?= .env
include $(DOTENV)
export

$(DOTENV):
	@touch $@


###################
# funções básicas #
.DEFAULT_GOAL := lib

.PHONY: lib
lib: $(LIBRARY)

.PHONY: build
build: clean-lib $(LIBRARY)

.PHONY: run
run: $(LIBRARY)
	@$(PYTHON) -O -m $(LIB)

##################
# funções de dev #
.PHONY: install
install: $(INSTALL)

.PHONY: tests
tests: $(TESTS)
	@echo All tests passed

.PHONY: docs
docs: $(LIBRARY) $(TESTS) $(DOCS)


###########################
# limpando (para refazer) #
.PHONY: clean
clean: clean-lib

.PHONY: clean-all
clean-all: clean-req clean-lib clean-tests clean-docs

.PHONY: clean-req
clean-req:
	@rm -f $(REQUIREMENTS)

.PHONY: clean-lib
clean-lib:
	@rm -rf $(LIBRARY) $(LIB_CACHE)

.PHONY: clean-tests
clean-tests:
	@rm -rf $(TESTS) $(TEST_CACHE)

.PHONY: clean-docs
clean-docs:
	@make -C $(DOCS_DIR) clean


######################
# chaves de controle #
$(REQUIREMENTS): requirements.txt
	@$(PIP) install --user -r $<
	@touch $@

$(LIBRARY): $(REQUIREMENTS) $(LIB_FILES)
	@echo Building lib...
	@$(PYTHON) -O -c "import $(LIB_DIR)"
	@touch $@

$(INSTALL): $(LIBRARY)
	@$(PIP) install --user .
	@touch $@

$(DEV_REQS): requirements-dev.txt $(REQUIREMENTS)
	@$(PIP) install --user -r $<
	@touch $@

$(TESTS): $(INSTALL) $(TEST_FILES) $(DEV_REQS)
	@$(TESTER) $(TEST_DIR)
	@touch $@

$(DOCS): $(LIBRARY) $(TESTS) $(DOCS_FILES)
	@make -C $(DOCS_DIR) $(DOCS_TYPE)
	@touch $@
