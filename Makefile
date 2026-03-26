PACKAGE         := rigolwfm
PACKAGE_DIR     := RigolWFM
GITHUB_USER     := scottprahl
REPO_NAME       := $(notdir $(CURDIR))

PY_VERSION      ?= 3.14
UV              ?= uv
RUN             := $(UV) run --extra dev
RUN_DOCS        := $(UV) run --extra docs
RUN_LITE        := $(UV) run --extra lite
RM              ?= rm -f
RMR             ?= rm -rf

KSC             ?= kaitai-struct-compiler
YAML_LINT_OPTS  := -d "{extends: default, rules: {document-start: disable, line-length: {max: 120}}}"

DOCS_DIR        := docs
HTML_DIR        := $(DOCS_DIR)/_build/html
JS_DIR          := wfmview
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
LAB_DISPLAY     := $(REPO_NAME) (.venv)

SPHINX_OPTS     := -T -E -b html -d $(DOCS_DIR)/_build/doctrees -D language=en
PYTEST_OPTS     :=

KSY_FILES       := $(wildcard ksy/*.ksy)
PYTHON_PARSERS  := $(patsubst ksy/%.ksy,$(PACKAGE_DIR)/%.py,$(KSY_FILES))
JS_PARSERS      := $(patsubst ksy/%.ksy,$(JS_DIR)/%.js,$(KSY_FILES))


PYLINT_TARGETS  := $(PACKAGE_DIR)/*.py tests/*.py .github/scripts/update_citation.py
PYDOC_TARGETS   := $(PACKAGE_DIR)/wfm.py $(PACKAGE_DIR)/channel.py $(PACKAGE_DIR)/wfmconvert.py
YAML_TARGETS    := .github/workflows/*.yaml .readthedocs.yaml
RST_TARGETS     := README.rst CHANGELOG.rst $(DOCS_DIR)/index.rst $(DOCS_DIR)/changelog.rst


.PHONY: help
help:
	@echo "Build Targets:"
	@echo "  all            - Generate parser code from all .ksy files"
	@echo "  dist           - Build sdist+wheel locally"
	@echo "  html           - Build Sphinx HTML documentation"
	@echo "  venv           - Install dependencies with uv"
	@echo "  lab            - Launch JupyterLab with a repo-local kernel"
	@echo ""
	@echo "Quality Targets:"
	@echo "  rcheck         - Run full release checks"
	@echo "  manifest-check  - Run MANIFEST.in checks"
	@echo "  pylint-check    - Run pylint checks"
	@echo "  pyroma-check    - Run pyroma checks"
	@echo "  ruff-check      - Run ruff checks"
	@echo "  rst-check       - Lint rst files"
	@echo "  yaml-check      - Lint ksy and workflow YAML files"
	@echo ""
	@echo "Test Targets:"
	@echo "  test           - Run all waveform conversion checks"
	@echo "  note-test      - Run notebook check"
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
	$(KSC) -t python --outdir $(PACKAGE_DIR) $<

.PHONY: js
js: $(JS_PARSERS)

$(JS_DIR)/%.js: ksy/%.ksy
	$(KSC) -t javascript --outdir $(JS_DIR) $<

.PHONY: html
html: $(PYTHON_PARSERS)
	@mkdir -p "$(HTML_DIR)"
	$(RUN_DOCS) sphinx-build $(SPHINX_OPTS) "$(DOCS_DIR)" "$(HTML_DIR)"
	@command -v open >/dev/null 2>&1 && open "$(HTML_DIR)/index.html" || true

.PHONY: lab
lab: venv lab-kernel
	@echo "==> Launching JupyterLab with repo-local kernel"
	JUPYTER_PREFER_ENV_PATH=1 $(RUN) jupyter lab --ServerApp.root_dir="$(CURDIR)"

.PHONY: lab-kernel
lab-kernel:
	@echo "==> Registering Jupyter kernel $(LAB_DISPLAY)"
	$(RUN) python -m ipykernel install --prefix "$(CURDIR)/.venv" --name python3 --display-name "$(LAB_DISPLAY)"

.PHONY: yaml-check
yaml-check:
	@$(RUN) yamllint $(YAML_LINT_OPTS) $(KSY_FILES)
	@$(RUN) yamllint $(YAML_TARGETS)

.PHONY: rst-check
rst-check:
	@$(RUN) rstcheck $(RST_TARGETS)
	@$(RUN) rstcheck --ignore-directives automodapi $(DOCS_DIR)/$(PACKAGE_DIR).rst

.PHONY: ksy-check
ksy-check:
	@$(RUN) ksylint $(KSY_FILES)

.PHONY: pylint-check
pylint-check:
	@$(RUN) pylint $(PYLINT_TARGETS)

.PHONY: ruff-check
ruff-check:
	@$(RUN) ruff check .

.PHONY: manifest-check
manifest-check:
	@$(RUN) check-manifest

.PHONY: pyroma-check
pyroma-check:
	@$(RUN) pyroma -d .

.PHONY: mypy-check
mypy-check:
	@$(RUN) mypy

.PHONY: test
test: $(PYTHON_PARSERS)
	$(RUN) pytest $(PYTEST_OPTS) tests --ignore=tests/test_all_notebooks.py

.PHONY: note-test
note-test: $(PYTHON_PARSERS)
	$(RUN) pytest --verbose tests/test_all_notebooks.py

.PHONY: rcheck
rcheck: realclean
	@echo "Running all release checks..."
	@$(MAKE) all
	@$(MAKE) yaml-check
	@$(MAKE) rst-check
	@$(MAKE) pylint-check
	@$(MAKE) mypy-check
	@$(MAKE) manifest-check
	@$(MAKE) pyroma-check
	@$(MAKE) html
	@$(MAKE) lite
	@$(MAKE) dist
	@$(MAKE) test
	@$(MAKE) note-test
	@echo "Release checks complete"

.PHONY: lite
lite: lite-clean $(LITE_CONFIG) dist
	@echo "==> Staging notebooks from $(DOCS_DIR) -> $(STAGE_DIR)"
	@mkdir -p "$(STAGE_DIR)"
	cp "$(DOCS_DIR)"/*.ipynb "$(STAGE_DIR)"
	$(RUN) jupyter nbconvert --clear-output --inplace "$(STAGE_DIR)"/*.ipynb
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

.PHONY: lite-clean
lite-clean:
	@$(RMR) "$(STAGE_DIR)"
	@$(RMR) "$(OUT_ROOT)"
	@$(RMR) "$(DOIT_DB)"
	@$(RMR) .cache dist $(PACKAGE_DIR).egg-info

.PHONY: clean
clean: lite-clean
	@find . -name '__pycache__' -type d -exec $(RMR) {} +
	@find . -name '.DS_Store' -type f -exec $(RM) {} +
	@find . -name '.ipynb_checkpoints' -type d -prune -exec $(RMR) {} +
	@find . -name '.pytest_cache' -type d -prune -exec $(RMR) {} +
	@$(RMR) build docs/_build docs/api docs/.jupyter docs/github.com docs/raw.githubusercontent.com docs/media.githubusercontent.com
	@$(RMR) .ruff_cache $(PACKAGE_DIR).egg-info
	@$(RM) wfm/*.sr

.PHONY: realclean
realclean: clean
	@git worktree remove "$(WORKTREE)" --force 2>/dev/null || true
	@git worktree prune || true
	@$(RMR) "$(WORKTREE)"
	@$(RMR) .venv
	@$(RMR) docs/github.com
	@$(RM) uv.lock
	@$(RM) $(PYTHON_PARSERS)

