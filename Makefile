.DEFAULT_GOAL := install

BIN_DIR=/usr/local/bin
DEPS_DIR=deps
PATCH_DIR=patches

deps-dir:
	if [ ! -d "./$(DEPS_DIR)" ]; then \
		mkdir $(DEPS_DIR); \
	fi

alexis-ccminer: deps-dir
	if [ ! -d "./$(DEPS_DIR)/alexis_ccminer" ]; then \
		git clone https://github.com/alexis78/ccminer.git $(DEPS_DIR)/alexis_ccminer && \
		cd $(DEPS_DIR)/alexis_ccminer && \
		git checkout cb990068b97c1b4d226b91c16c6a0dfd5ef591ca && \
		git apply ../../$(PATCH_DIR)/alexis_patch && \
		./build.sh && \
		sudo cp ccminer $(BIN_DIR)/alexis-ccminer; \
	fi

tpruvot-ccminer: deps-dir
	if [ ! -d "./$(DEPS_DIR)/tpruvot_ccminer" ]; then \
		git clone https://github.com/tpruvot/ccminer.git $(DEPS_DIR)/tpruvot_ccminer && \
		cd $(DEPS_DIR)/tpruvot_ccminer && \
		git checkout 50781f00ebaab95ad578c6c37a8f7f44019ac7a6 && \
		git apply ../../$(PATCH_DIR)/tpruvot_patch && \
		./build.sh && \
		sudo cp ccminer $(BIN_DIR)/tpruvot-ccminer; \
	fi

vertminer: deps-dir
	if [ ! -d "./$(DEPS_DIR)/vertminer" ]; then \
		git clone https://github.com/vertcoin/vertminer-nvidia.git $(DEPS_DIR)/vertminer && \
		cd $(DEPS_DIR)/vertminer && \
		git checkout 3042aa21bedf15d9b9333750331d317705e2118d && \
		git apply ../../$(PATCH_DIR)/vertminer_patch && \
		./build.sh && \
		sudo cp vertminer $(BIN_DIR)/vertminer; \
	fi

deps: alexis-ccminer tpruvot-ccminer vertminer

install: deps
	sudo python3 setup.py install

run: install
	sudo miner -c /usr/local/etc/miner.conf

test:
	sudo python3 setup.py test

quickclean:
	sudo python3 setup.py clean

clean: quickclean
	sudo git clean -Xfd
	sudo rm -r $(DEPS_DIR) || true

distclean: clean
	sudo rm $(BIN_DIR)/alexis-ccminer || true
	sudo rm $(BIN_DIR)/tpruvot-ccminer || true
	sudo rm $(BIN_DIR)/vertminer || true
	sudo rm $(BIN_DIR)/miner || true
