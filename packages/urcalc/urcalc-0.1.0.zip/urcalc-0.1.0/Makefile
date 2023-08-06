# Copyright (C) 2014 by Yu-Jie Lin
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

PACKAGE = urcalc
SCRIPT  = c

PY_CMD = python3
PY_FILES = c $(wildcard *.py)

BUILD_CMD = setup.py sdist --formats gztar,zip bdist_wheel

INSTALL_TEST_DIR=/tmp/$(PACKAGE)_install_test

.PHONY: build
build: check .build
.build: $(PY_FILES) MANIFEST.in README.rst
	$(PY_CMD) $(BUILD_CMD)
	@touch $@

.PHONY: upload
upload: build
	$(PY_CMD) $(BUILD_CMD) upload

.PHONY: fix-isort
fix-isort:
	$(PY_CMD) -m isort.main $(PY_FILES)

.PHONY: check
check: check-codes check-tests check-setup

.PHONY: check-codes
check-codes: .check-codes
.check-codes: $(PY_FILES)
ifndef DISABLE_CHECK_CODES
ifndef DISABLE_CHECK_DOC8
	@echo '========================================================================================='
	$(PY_CMD) -m doc8.main *.rst
endif
ifndef DISABLE_CHECK_ISORT
	@echo '========================================================================================='
	@echo $(PY_CMD) -m isort.main $(PY_FILES)
	@ if ! $(PY_CMD) -m isort.main --check-only $(PY_FILES); then \
	  echo '-----------------------------------------------------------------------------------------'; \
	  $(PY_CMD) -m isort.main --diff $(PY_FILES); \
	  echo '-----------------------------------------------------------------------------------------'; \
	  echo run make fix-isort to commit these fixes; \
	  exit 1; \
	fi
endif
ifndef DISABLE_CHECK_PEP8
	@echo '========================================================================================='
	$(PY_CMD) -m pep8 $(PY_FILES)
endif
ifndef DISABLE_CHECK_PYFLAKES
	@echo '========================================================================================='
	$(PY_CMD) -m pyflakes $(PY_FILES)
endif
endif
	@touch $@

.PHONY: check-tests
check-tests: check-codes .check-tests
.check-tests: $(PY_FILES)
	@echo '========================================================================================='
	$(PY_CMD) tests.py
	@touch $@

.PHONY: check-setup
check-setup: check-codes .check-setup
.check-setup: $(PY_FILES) MANIFEST.in README.rst
	@echo '========================================================================================='
	rm -rf $(INSTALL_TEST_DIR)
	$(PY_CMD) -m virtualenv $(INSTALL_TEST_DIR)
	LC_ALL=C $(PY_CMD) setup.py --version >/dev/null
	$(PY_CMD) $(BUILD_CMD)
	$(PY_CMD) setup.py sdist --dist-dir $(INSTALL_TEST_DIR)
	$(INSTALL_TEST_DIR)/bin/pip install $(INSTALL_TEST_DIR)/*.tar.gz
	@ REQS="$$PWD"/requirements.txt;\
	  cd $(INSTALL_TEST_DIR); \
	  . bin/activate; \
	  $(INSTALL_TEST_DIR)/bin/pip install -r "$$REQS"; \
	  tar xf $(PACKAGE)-*.tar.gz; \
	  cd $(PACKAGE)-*; \
	  $(PY_CMD) tests.py
	@ CHK_VER="`$(PY_CMD) $(SCRIPT) --version 2>&1`"; \
	  cd $(INSTALL_TEST_DIR); \
	  . bin/activate; \
	  [ "`type $(SCRIPT)`" = "$(SCRIPT) is $(INSTALL_TEST_DIR)/bin/$(SCRIPT)" ] && \
	  [ "$$CHK_VER" = "`bin/$(SCRIPT) --version 2>&1`" ]
	rm -rf $(INSTALL_TEST_DIR)
	@touch $@

.PHONY: clean
clean:
	rm -f .build .check-*
	rm -rf __pycache__ build dist
