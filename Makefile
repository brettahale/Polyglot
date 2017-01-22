PY2C= \
	"polyglot/core.py" \
	"polyglot/config_manager.py" \
	"polyglot/nodeserver_manager.py" \
	"polyglot/nodeserver_api.py" \
	"polyglot/nodeserver_helpers.py"
CONFIG_DIR="/etc/polyglot"
INSTALL_DIR="/usr/local/lib"
BIN_DIR="/usr/local/bin"
DAEMON_USER="polyglot"
OS_NAME=$(shell uname)
PROC_NAME=$(shell uname -m)
PYTHON_LOCATION=$(shell which python)

ifeq ($(OS_NAME),Linux)
	BUILD_TYPE = .linux.$(PROC_NAME)
endif
ifeq ($(OS_NAME),Darwin)
	BUILD_TYPE = .osx.$(PROC_NAME)
endif
ifeq ($(OS_NAME),FreeBSD)
	BUILD_TYPE = .freebsd.$(PROC_NAME)
endif

UPX := $(shell command -v upx 2>/dev/null)

build: polyglot
	# "Removing pyc files and __pycache__ directories..."
	find . -name "*.pyc" -exec rm -rfv {} \;  # python 2
	find . -name "__pycache__" -exec rm -rfv {} \;  # python 3

	# "Making pyx files..."
	for file in $(PY2C); do \
		cp -v $$file $$file'x'; \
		sed -i -e 's/\# \[cython\] //g' $$file'x'; \
	done

	# "Compiling pyx files..."
	python setup.py build_ext --inplace
	
ifdef UPX
	# "Found UPX. Compressing Binaries."
	find "polyglot" -name "*.so" -exec upx -9 -q {} \;
else
	# "UPX Not Found. Skipping, not required."
endif
	
	# Exporting to build dirctory
	rm -rf build
	mkdir build
	cp -r polyglot build/

	# Cleaning up source
	find "polyglot" -name "*.c" -exec rm -rf {} \;
	find "polyglot" -name "*.so" -exec rm -rf {} \;
	find "polyglot" -name "*.pyx*" -exec rm -rf {} \;
	for file in $(PY2C); do \
		rm -v 'build/'$$file; \
	done

	# Clean build files
	find "build/polyglot" -name "*.c" -exec rm -rfv {} \;
	find "build/polyglot" -name "*.pyx*" -exec rm -rfv {} \;
	find "build/polyglot" -d -type d -name "CVS" -exec rm -Rfv {} \;

	# Install dependencies locally
	python -m pip install -r requirements.txt --target ./build

	# Create polyglot.pyz executable
	mkdir -p bin
	mv build/polyglot/__main__.py build/
	cd build; zip -r9q polyglot.zip *
	echo "#!$(PYTHON_LOCATION)" > build/shebang
	cat build/shebang build/polyglot.zip > bin/polyglot$(BUILD_TYPE).pyz
	chmod +x bin/polyglot$(BUILD_TYPE).pyz

	# Remove current build directory
	rm -rf build
