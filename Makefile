all: fishmake-libs
	@PYTHONPATH=${PYTHONPATH}:py-libs ./src/fishmake/src/main.py install --SKIP_UPDATE True

init: clone-libs install-libs
	
update: update-libs install-libs

clone-libs:
	@mkdir -p py-deps
	@git clone git+ssh://git.rleszilm.com/data/git/pybase.git py-deps/pybase
	@git clone git+ssh://git.rleszilm.com/data/git/pyrcs.git  py-deps/pyrcs
	@git clone git+ssh://git.rleszilm.com/data/git/pyerl.git  py-deps/pyerl

fishmake-libs:
	@rm -rf py-libs/fishmake
	@mkdir -p py-libs/fishmake
	@cp -r src/fishmake/src/* py-libs/fishmake

install-libs:
	@mkdir -p py-libs
	@mkdir -p py-libs/pybase
	@mkdir -p py-libs/pyerl
	@mkdir -p py-libs/pyrcs
	@cp -r py-deps/pybase/src/* py-libs/pybase
	@cp -r py-deps/pyerl/src/*  py-libs/pyerl
	@cp -r py-deps/pyrcs/src/*  py-libs/pyrcs

update-libs:
	@cd py-deps/pybase && git update
	@cd py-deps/pyerl  && git update
	@cd py-deps/pyrcs  && git update