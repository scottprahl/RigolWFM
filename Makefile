PACKAGE         := rigolwfm
PACKAGE_DIR     := RigolWFM
GITHUB_USER     := scottprahl

PY_VERSION      ?= 3.14
UV              ?= uv
RUN             := $(UV) run --extra dev
RUN_DOCS        := $(UV) run --extra docs
RUN_LITE        := $(UV) run --extra lite
RM              ?= rm -f
RMR             ?= rm -rf

KSC             ?= kaitai-struct-compiler
KSY_OPTIONS     := --outdir $(PACKAGE_DIR)
KSY_PY_OPTIONS  := -t python $(KSY_OPTIONS)
YAML_LINT_OPTS  := -d "{extends: default, rules: {document-start: disable}}"

DOCS_DIR        := docs
HTML_DIR        := $(DOCS_DIR)/_build/html
OUT_ROOT        := _site
OUT_DIR         := $(OUT_ROOT)/$(PACKAGE)
STAGE_DIR       := .lite_src
DOIT_DB         := .jupyterlite.doit.db
LITE_CONFIG     := $(PACKAGE_DIR)/jupyter_lite_config.json

PAGES_BRANCH    := gh-pages
WORKTREE        := .gh-pages
REMOTE          := origin

HOST            := 127.0.0.1
PORT            := 8000

SPHINX_OPTS     := -T -E -b html -d $(DOCS_DIR)/_build/doctrees -D language=en
PYTEST_OPTS     :=

KSY_FILES       := \
	ksy/wfm1000b.ksy \
	ksy/wfm1000c.ksy \
	ksy/wfm1000d.ksy \
	ksy/wfm1000e.ksy \
	ksy/wfm1000z.ksy \
	ksy/wfm2000.ksy \
	ksy/wfm4000.ksy \
	ksy/wfm6000.ksy

PYTHON_PARSERS  := $(KSY_FILES:ksy/%.ksy=$(PACKAGE_DIR)/%.py)
PYLINT_TARGETS  := $(PACKAGE_DIR)/*.py tests/*.py .github/scripts/update_citation.py
PYDOC_TARGETS   := $(PACKAGE_DIR)/wfm.py $(PACKAGE_DIR)/channel.py $(PACKAGE_DIR)/wfmconvert.py
YAML_TARGETS    := .github/workflows/citation.yaml .github/workflows/pypi.yaml .github/workflows/test.yaml .readthedocs.yaml
RST_TARGETS     := README.rst CHANGELOG.rst $(DOCS_DIR)/index.rst $(DOCS_DIR)/changelog.rst

TEST_B_FILES    := wfm/DS1204B-A.wfm wfm/DS1204B-B.wfm wfm/DS1204B-C.wfm wfm/DS1204B-D.wfm wfm/DS1204B-E.wfm
TEST_C_FILES    := wfm/DS1202CA-A.wfm wfm/DS1042C-A.wfm
TEST_D_FILES    := wfm/DS1102D-A.wfm
TEST_E_FILES    := wfm/DS1102E-A.wfm wfm/DS1102E-B.wfm wfm/DS1102E-C.wfm wfm/DS1102E-D.wfm wfm/DS1102E-E.wfm wfm/DS1102E-F.wfm wfm/DS1102E-G.wfm wfm/DS1052E.wfm wfm/DS1000E-A.wfm wfm/DS1000E-B.wfm wfm/DS1000E-C.wfm wfm/DS1000E-D.wfm
TEST_Z_FILES    := wfm/DS1074Z-C.wfm wfm/DS1054Z-A.wfm wfm/MSO1104.wfm wfm/DS1074Z-A.wfm wfm/DS1074Z-B.wfm
TEST_2_FILES    := wfm/DS2072A-1.wfm wfm/DS2072A-2.wfm wfm/DS2072A-3.wfm wfm/DS2072A-4.wfm wfm/DS2072A-5.wfm wfm/DS2072A-6.wfm wfm/DS2072A-7.wfm wfm/DS2072A-8.wfm wfm/DS2072A-9.wfm wfm/DS2000-A.wfm wfm/DS2000-B.wfm
TEST_4_FILES    := wfm/DS4022-A.wfm wfm/DS4022-B.wfm wfm/DS4024-A.wfm wfm/DS4024-B.wfm

CONVERT_CASES   := E:wfm/DS1102E-A.wfm Z:wfm/MSO1104.wfm 4:wfm/DS4022-A.wfm 2:wfm/DS2202.wfm C:wfm/DS1202CA-A.wfm B:wfm/DS1204B-A.wfm D:wfm/DS1102D-A.wfm

CLEANTEST_FILES := \
	wfm/DS1102E-A.csv wfm/DS1102E-A.wav wfm/DS1102E-A.vcsv wfm/DS1102E-A.sr \
	wfm/MSO1104.csv wfm/MSO1104.wav wfm/MSO1104.vcsv wfm/MSO1104.sr \
	wfm/DS4022-A.csv wfm/DS4022-A.wav wfm/DS4022-A.vcsv wfm/DS4022-A.sr \
	wfm/DS2202.csv wfm/DS2202.wav wfm/DS2202.vcsv wfm/DS2202.sr \
	wfm/DS1202CA-A.csv wfm/DS1202CA-A.wav wfm/DS1202CA-A.vcsv wfm/DS1202CA-A.sr \
	wfm/DS1204B-A.csv wfm/DS1204B-A.wav wfm/DS1204B-A.vcsv wfm/DS1204B-A.sr \
	wfm/DS1202Z-1.csv wfm/DS1202Z-1.png wfm/DS1202Z-1.txt wfm/DS1202Z-1.wfm \
	wfm/DS1202Z-2.csv wfm/DS1202Z-2.png wfm/DS1202Z-2.txt wfm/DS1202Z-2.wfm \
	wfm/DS1102D-A.sr wfm/DS1102D-A.vcsv wfm/DS1102D-A.wav

.PHONY: help
help:
	@echo "Build Targets:"
	@echo "  all            - Generate parser code from all .ksy files"
	@echo "  dist           - Build sdist+wheel locally"
	@echo "  html           - Build Sphinx HTML documentation"
	@echo "  venv           - Install dependencies with uv"
	@echo ""
	@echo "Quality Targets:"
	@echo "  yamlcheck      - Lint ksy and workflow YAML files"
	@echo "  rstcheck       - Lint rst files"
	@echo "  ksycheck       - Lint ksy schema files"
	@echo "  pycheck        - Run pylint/pydocstyle/ruff checks"
	@echo "  rcheck         - Run full release checks"
	@echo ""
	@echo "Test Targets:"
	@echo "  test           - Run all waveform conversion checks"
	@echo "  testtests      - Run pytest suite"
	@echo ""
	@echo "JupyterLite Targets:"
	@echo "  lite           - Build JupyterLite output into $(OUT_DIR)"
	@echo "  lite-serve     - Serve $(OUT_ROOT) at http://$(HOST):$(PORT)"
	@echo "  lite-deploy    - Deploy $(OUT_DIR) to $(PAGES_BRANCH)"
	@echo "  lite-clean     - Remove JupyterLite build artifacts"
	@echo ""
	@echo "Cleanup Targets:"
	@echo "  clean          - Remove generated test/build/doc artifacts"
	@echo "  realclean      - clean + remove generated parser files"

.PHONY: venv
venv:
	@$(UV) sync --python $(PY_VERSION) --extra dev --extra docs --extra lite

.PHONY: all
all: $(PYTHON_PARSERS)

$(PACKAGE_DIR)/%.py: ksy/%.ksy
	$(KSC) $(KSY_PY_OPTIONS) $<

.PHONY: dist
dist:
	$(RUN) python -m build

.PHONY: html
html:
	@mkdir -p "$(HTML_DIR)"
	$(RUN_DOCS) sphinx-build $(SPHINX_OPTS) "$(DOCS_DIR)" "$(HTML_DIR)"
	@command -v open >/dev/null 2>&1 && open "$(HTML_DIR)/index.html" || true

.PHONY: yamlcheck yaml-check
yamlcheck yaml-check:
	@$(RUN) yamllint $(YAML_LINT_OPTS) $(KSY_FILES)
	@$(RUN) yamllint $(YAML_TARGETS)

.PHONY: rstcheck rst-check
rstcheck rst-check:
	@$(RUN) rstcheck $(RST_TARGETS)
	@$(RUN) rstcheck --ignore-directives automodapi $(DOCS_DIR)/$(PACKAGE_DIR).rst

.PHONY: ksycheck
ksy-check:
	@$(RUN) ksylint $(KSY_FILES)

.PHONY: pylint-check
pylint-check:
	@$(RUN) pylint $(PYLINT_TARGETS)

.PHONY: pydocstyle-check
pydocstyle-check:
	@$(RUN) pydocstyle $(PYDOC_TARGETS)

.PHONY: ruff-check
ruff-check:
	@$(RUN) ruff check .

.PHONY: pycheck
pycheck: pylint-check pydocstyle-check ruff-check

.PHONY: manifest-check
manifest-check:
	@$(RUN) check-manifest

.PHONY: pyroma-check
pyroma-check:
	@$(RUN) pyroma -d .

.PHONY: testb
testb:
	@for f in $(TEST_B_FILES); do $(RUN) wfmconvert B info $$f; done

.PHONY: testc
testc:
	@for f in $(TEST_C_FILES); do $(RUN) wfmconvert C info $$f; done

.PHONY: testd
testd:
	@for f in $(TEST_D_FILES); do $(RUN) wfmconvert D info $$f; done

.PHONY: teste
teste:
	@for f in $(TEST_E_FILES); do $(RUN) wfmconvert E info $$f; done

.PHONY: testz
testz:
	@for f in $(TEST_Z_FILES); do $(RUN) wfmconvert Z info $$f; done

.PHONY: test2
test2:
	@for f in $(TEST_2_FILES); do $(RUN) wfmconvert 2 info $$f; done

.PHONY: test4
test4:
	@for f in $(TEST_4_FILES); do $(RUN) wfmconvert 4 info $$f; done

.PHONY: csv
csv:
	@for item in $(CONVERT_CASES); do \
		scope=$${item%%:*}; file=$${item#*:}; \
		$(RUN) wfmconvert $$scope csv $$file; \
	done

.PHONY: wav
wav:
	@for item in $(CONVERT_CASES); do \
		scope=$${item%%:*}; file=$${item#*:}; \
		$(RUN) wfmconvert $$scope wav $$file; \
	done

.PHONY: vcsv
vcsv:
	@for item in $(CONVERT_CASES); do \
		scope=$${item%%:*}; file=$${item#*:}; base=$${file%.wfm}; \
		$(RUN) wfmconvert $$scope vcsv $$file; \
		mv $$base.csv $$base.vcsv; \
	done

.PHONY: sigrok
sigrok:
	@echo "*********************************************************"
	@echo "*** conversion works despite warning about /dev/stdin ***"
	@echo "*********************************************************"
	@for item in $(CONVERT_CASES); do \
		scope=$${item%%:*}; file=$${item#*:}; \
		$(RUN) wfmconvert $$scope sigrok $$file; \
	done

.PHONY: testtests note-test
testtests note-test:
	$(RUN) pytest --verbose tests/test_wfmconvert.py
	$(RUN) pytest --verbose tests/test_wfmconvert_sigrok.py
	$(RUN) pytest --verbose tests/test_all_notebooks.py

.PHONY: test
test: $(PYTHON_PARSERS)
	@$(MAKE) testd
	@$(MAKE) teste
	@$(MAKE) testz
	@$(MAKE) test4
	@$(MAKE) test2
	@$(MAKE) testc
	@$(MAKE) vcsv
	@$(MAKE) csv
	@$(MAKE) wav
	@$(MAKE) sigrok
	@$(MAKE) testtests

.PHONY: rcheck
rcheck:
	@echo "Running all release checks..."
	@$(MAKE) realclean
	@$(MAKE) all
#	@$(MAKE) ksy-check
	@$(MAKE) yaml-check
	@$(MAKE) rst-check
	@$(MAKE) pylint-check
	@$(MAKE) manifest-check
	@$(MAKE) pyroma-check
	@$(MAKE) html
	@$(MAKE) lite
	@$(MAKE) dist
	@$(MAKE) test
	@echo "Release checks complete"

.PHONY: lite
lite: lite-clean $(LITE_CONFIG) dist
	@echo "==> Staging notebooks from $(DOCS_DIR) -> $(STAGE_DIR)"
	@mkdir -p "$(STAGE_DIR)"
	cp "$(DOCS_DIR)"/*.ipynb "$(STAGE_DIR)"
	$(RUN) python -m jupyter nbconvert --clear-output --inplace "$(STAGE_DIR)"/*.ipynb
	@echo "==> Building JupyterLite"
	@$(RUN_LITE) jupyter lite build \
		--config="$(LITE_CONFIG)" \
		--contents="$(STAGE_DIR)" \
		--output-dir="$(OUT_DIR)"
	@touch "$(OUT_DIR)/.nojekyll"

.PHONY: lite-serve
lite-serve:
	@test -d "$(OUT_DIR)" || { echo "run 'make lite' first"; exit 1; }
	@echo "Serving JupyterLite at http://$(HOST):$(PORT)/$(PACKAGE)/?disableCache=1"
	$(RUN_LITE) python -m http.server -d "$(OUT_ROOT)" --bind $(HOST) $(PORT)

.PHONY: lite-deploy
lite-deploy:
	@test -d "$(OUT_DIR)" || { echo "Run 'make lite' first"; exit 1; }
	@if ! git show-ref --verify --quiet refs/heads/$(PAGES_BRANCH); then \
		CURRENT=$$(git branch --show-current); \
		git switch --orphan $(PAGES_BRANCH); \
		git commit --allow-empty -m "Initialize $(PAGES_BRANCH)"; \
		git switch $$CURRENT; \
	fi
	@git worktree remove "$(WORKTREE)" --force 2>/dev/null || true
	@git worktree prune || true
	@$(RMR) "$(WORKTREE)"
	@git worktree add "$(WORKTREE)" "$(PAGES_BRANCH)"
	@git -C "$(WORKTREE)" pull "$(REMOTE)" "$(PAGES_BRANCH)" 2>/dev/null || true
	@rsync -a --delete --exclude ".git*" "$(OUT_DIR)/" "$(WORKTREE)/"
	@touch "$(WORKTREE)/.nojekyll"
	@date -u +"%Y-%m-%d %H:%M:%S UTC" > "$(WORKTREE)/.pages-ping"
	@cd "$(WORKTREE)" && \
		git add -A && \
		if git diff --quiet --cached; then \
			echo "No changes to deploy"; \
		else \
			git commit -m "Deploy $$(date -u +'%Y-%m-%d %H:%M:%S UTC')" && \
			git push "$(REMOTE)" "$(PAGES_BRANCH)" && \
			echo "Deployed to https://$(GITHUB_USER).github.io/$(PACKAGE)/"; \
		fi

.PHONY: run
run: lite lite-serve

.PHONY: cleantest
cleantest:
	@$(RMR) $(CLEANTEST_FILES)

.PHONY: lite-clean
lite-clean:
	@$(RMR) "$(STAGE_DIR)"
	@$(RMR) "$(OUT_ROOT)"
	@$(RMR) "$(DOIT_DB)"
	@$(RMR) .cache dist $(PACKAGE_DIR).egg-info

.PHONY: clean
clean: lite-clean
	@$(MAKE) cleantest
	@find . -name '__pycache__' -type d -exec $(RMR) {} +
	@find . -name '.DS_Store' -type f -exec $(RM) {} +
	@find . -name '.ipynb_checkpoints' -type d -prune -exec $(RMR) {} +
	@find . -name '.pytest_cache' -type d -prune -exec $(RMR) {} +
	@$(RMR) build docs/_build docs/api docs/.jupyter docs/github.com docs/raw.githubusercontent.com docs/media.githubusercontent.com
	@$(RMR) .ruff_cache $(PACKAGE_DIR).egg-info tests/*.csv tests/*.wav tests/*.sr

.PHONY: realclean
realclean: clean
	@git worktree remove "$(WORKTREE)" --force 2>/dev/null || true
	@git worktree prune || true
	@$(RMR) "$(WORKTREE)"
	@$(RMR) .venv
	@$(RM) uv.lock
	@$(RM) $(PYTHON_PARSERS)
