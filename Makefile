# MAKEFILE
#
# @author      Nicola Asuni <info@tecnick.com>
# @link        https://github.com/bits-and-blooms/bloom
# ------------------------------------------------------------------------------

# List special make targets that are not associated with files
.PHONY: help all test format fmtcheck vet lint coverage cyclo ineffassign misspell structcheck varcheck errcheck gosimple astscan qa deps clean nuke

# Use bash as shell (Note: Ubuntu now uses dash which doesn't support PIPESTATUS).
SHELL=/bin/bash

# CVS path (path to the parent dir containing the project)
CVSPATH=github.com/bits-and-blooms

# Project owner
OWNER=bits-and-blooms

# Project vendor
VENDOR=bits-and-blooms

# Project name
PROJECT=bloom

# Conda env name
CONDA_ENV_NAME=bloom

# Project version
VERSION=$(shell cat VERSION)

# Name of RPM or DEB package
PKGNAME=${VENDOR}-${PROJECT}

# Current directory
CURRENTDIR=$(shell pwd)

# GO lang path
ifneq ($(GOPATH),)
	ifeq ($(findstring $(GOPATH),$(CURRENTDIR)),)
		# the defined GOPATH is not valid
		GOPATH=
	endif
endif
ifeq ($(GOPATH),)
	# extract the GOPATH
	GOPATH=$(firstword $(subst /src/, ,$(CURRENTDIR)))
endif

CONDA_ACTIVATE=source $$(conda info --base)/etc/profile.d/conda.sh ; conda activate ; conda activate

# --- MAKE TARGETS ---

# Display general help about this command
help:       
	@echo ""
	@echo "$(PROJECT) Makefile."
	@echo "GOPATH=$(GOPATH)"
	@echo "The following commands are available:"
	@echo ""
	@echo "    make qa                 : Run all the tests"
	@echo "    make test               : Run the unit tests"
	@echo ""
	@echo "    make format             : Format the source code"
	@echo "    make fmtcheck           : Check if the source code has been formatted"
	@echo "    make vet                : Check for suspicious constructs"
	@echo "    make lint               : Check for style errors"
	@echo "    make coverage           : Generate the coverage report"
	@echo "    make cyclo              : Generate the cyclomatic complexity report"
	@echo "    make ineffassign        : Detect ineffectual assignments"
	@echo "    make misspell           : Detect commonly misspelled words in source files"
	@echo "    make structcheck        : Find unused struct fields"
	@echo "    make varcheck           : Find unused global variables and constants"
	@echo "    make errcheck           : Check that error return values are used"
	@echo "    make gosimple           : Suggest code simplifications"
	@echo "    make astscan            : GO AST scanner"
	@echo ""
	@echo "    make docs               : Generate source code documentation"
	@echo ""
	@echo "    make deps               : Get the dependencies"
	@echo "    make clean              : Remove any build artifact"
	@echo "    make nuke               : Deletes any intermediate file"
	@echo ""
	@echo "    make python-environment : Install conda env and deps for Python package"
	@echo "    make python-lint-apply  : Apply linting rules against the Python files"
	@echo "    make python-lint-check  : Check the diff after applying the linting rules against the Python files"
	@echo "    make python-build       : Build the external module, source and the binary distributions of the Python package"
	@echo "    make python-install     : Install the Python package in editable mode"
	@echo "    make python-tests       : Run the tests on the installed version of the Python package"

# Alias for help target
all: help

# Run the unit tests
test:
	@mkdir -p target/test
	@mkdir -p target/report
	GOPATH=$(GOPATH) \
	go test \
	-covermode=atomic \
	-bench=. \
	-race \
	-cpuprofile=target/report/cpu.out \
	-memprofile=target/report/mem.out \
	-mutexprofile=target/report/mutex.out \
	-coverprofile=target/report/coverage.out \
	-v ./... | \
	tee >(PATH=$(GOPATH)/bin:$(PATH) go-junit-report > target/test/report.xml); \
	test $${PIPESTATUS[0]} -eq 0

# Format the source code
format:
	@find . -type f -name "*.go" -exec gofmt -s -w {} \;

# Check if the source code has been formatted
fmtcheck:
	@mkdir -p target
	@find . -type f -name "*.go" -exec gofmt -s -d {} \; | tee target/format.diff
	@test ! -s target/format.diff || { echo "ERROR: the source code has not been formatted - please use 'make format' or 'gofmt'"; exit 1; }

# Check for syntax errors
vet:
	GOPATH=$(GOPATH) go vet .

# Check for style errors
lint:
	GOPATH=$(GOPATH) PATH=$(GOPATH)/bin:$(PATH) golint .

# Generate the coverage report
coverage:
	@mkdir -p target/report
	GOPATH=$(GOPATH) \
	go tool cover -html=target/report/coverage.out -o target/report/coverage.html

# Report cyclomatic complexity
cyclo:
	@mkdir -p target/report
	GOPATH=$(GOPATH) gocyclo -avg ./ | tee target/report/cyclo.txt ; test $${PIPESTATUS[0]} -eq 0

# Detect ineffectual assignments
ineffassign:
	@mkdir -p target/report
	GOPATH=$(GOPATH) ineffassign ./ | tee target/report/ineffassign.txt ; test $${PIPESTATUS[0]} -eq 0

# Detect commonly misspelled words in source files
misspell:
	@mkdir -p target/report
	GOPATH=$(GOPATH) misspell -error ./  | tee target/report/misspell.txt ; test $${PIPESTATUS[0]} -eq 0

# Find unused struct fields
structcheck:
	@mkdir -p target/report
	GOPATH=$(GOPATH) structcheck -a ./  | tee target/report/structcheck.txt

# Find unused global variables and constants
varcheck:
	@mkdir -p target/report
	GOPATH=$(GOPATH) varcheck -e ./  | tee target/report/varcheck.txt

# Check that error return values are used
errcheck:
	@mkdir -p target/report
	GOPATH=$(GOPATH) errcheck ./  | tee target/report/errcheck.txt

# Suggest code simplifications
gosimple:
	@mkdir -p target/report
	GOPATH=$(GOPATH) gosimple ./  | tee target/report/gosimple.txt

# AST scanner
astscan:
	@mkdir -p target/report
	GOPATH=$(GOPATH) gas .//*.go | tee target/report/astscan.txt ; test $${PIPESTATUS[0]} -eq 0

# Generate source docs
docs:
	@mkdir -p target/docs
	nohup sh -c 'GOPATH=$(GOPATH) godoc -http=127.0.0.1:6060' > target/godoc_server.log 2>&1 &
	wget --directory-prefix=target/docs/ --execute robots=off --retry-connrefused --recursive --no-parent --adjust-extension --page-requisites --convert-links http://127.0.0.1:6060/pkg/github.com/${VENDOR}/${PROJECT}/ ; kill -9 `lsof -ti :6060`
	@echo '<html><head><meta http-equiv="refresh" content="0;./127.0.0.1:6060/pkg/'${CVSPATH}'/'${PROJECT}'/index.html"/></head><a href="./127.0.0.1:6060/pkg/'${CVSPATH}'/'${PROJECT}'/index.html">'${PKGNAME}' Documentation ...</a></html>' > target/docs/index.html

# Alias to run all quality-assurance checks
qa: fmtcheck test vet lint coverage cyclo ineffassign misspell structcheck varcheck errcheck gosimple astscan

# --- INSTALL ---

# Get the dependencies
deps:
	GOPATH=$(GOPATH) go get ./...
	GOPATH=$(GOPATH) go get github.com/golang/lint/golint
	GOPATH=$(GOPATH) go get github.com/jstemmer/go-junit-report
	GOPATH=$(GOPATH) go get github.com/axw/gocov/gocov
	GOPATH=$(GOPATH) go get github.com/fzipp/gocyclo
	GOPATH=$(GOPATH) go get github.com/gordonklaus/ineffassign
	GOPATH=$(GOPATH) go get github.com/client9/misspell/cmd/misspell
	GOPATH=$(GOPATH) go get github.com/opennota/check/cmd/structcheck
	GOPATH=$(GOPATH) go get github.com/opennota/check/cmd/varcheck
	GOPATH=$(GOPATH) go get github.com/kisielk/errcheck
	GOPATH=$(GOPATH) go get honnef.co/go/tools/cmd/gosimple
	GOPATH=$(GOPATH) go get github.com/securego/gosec

# Remove any build artifact
clean:
	GOPATH=$(GOPATH) go clean ./...

# Deletes any intermediate file
nuke:
	rm -rf target dist build python/shaped_bloom_filter.egg-info __pycache__
	GOPATH=$(GOPATH) go clean -i ./...

# Install the conda environment
python-environment:
	$(CONDA_ACTIVATE) $(CONDA_ENV_NAME) || conda create -n $(CONDA_ENV_NAME) -c conda-forge python=3.9 -y
	$(CONDA_ACTIVATE) $(CONDA_ENV_NAME) && pip install setuptools setuptools-golang wheel pytest black isort

# Apply linting rules against the Python files
python-lint-apply:
	$(CONDA_ACTIVATE) $(CONDA_ENV_NAME) && \
		black . --color --line-length 88 --target-version py39 && \
		isort . --profile black --line-length 88
		
# Check linting rules against the Python files
python-lint-check:
	$(CONDA_ACTIVATE) $(CONDA_ENV_NAME) && \
		black . --diff --color --check --line-length 88 --target-version py39 && \
		isort . --profile black --line-length 88 --diff -c
		
# Build shaped-bloom-filter package (extension, source/binary distributions)
python-build:
	rm -rf dist build target wheelhouse python/shaped_bloom_filter.egg-info python/shaped_bloom_filter/libbloomf*.so
	$(CONDA_ACTIVATE) $(CONDA_ENV_NAME) && GOPATH= python setup.py build_ext sdist bdist

# Install shaped-bloom-filter package in editable mode
python-install:
	rm -rf dist build target wheelhouse python/shaped_bloom_filter.egg-info python/shaped_bloom_filter/libbloomf*.so
	$(CONDA_ACTIVATE) $(CONDA_ENV_NAME) && GOPATH= pip install --force-reinstall -e .

# Run shaped-bloom-filter tests
python-tests:
	$(CONDA_ACTIVATE) $(CONDA_ENV_NAME) && pytest -v -s python/tests/*.py
