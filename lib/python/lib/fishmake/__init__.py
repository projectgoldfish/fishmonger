from fishmake.compiler  import compile   as compile
from fishmake.configure import configure as configure
from fishmake.installer import install   as install

import fishmake.languages

usableLanguages = []
for c in fishmake.languages.available():
	lang = __import__("fishmake.languages." + c)
	exec("usableLanguages.append(lang.languages." + c + ")")

import pybase.git    as PyGit

## Directories that a built app should contain.
NIXDirs  = ["bin", "doc", "etc", "lib", "lib/erlang/lib", "log", "sbin", "var", "var/run"]

## Initialize config
Defaults = [
	("APP_ID",           PyGit.getId()),
	("APP_DIRS",         ""),
	("APP_MAIN",         False),
	("APP_NAME",         False),
	("APP_COOKIE",       "snickerdoodle"),
	("APP_VERSION",      PyGit.getVersion()),
	
	## CXX
	("CXX_COMPILER",     "g++"),
	("CXX_FLAGS",        ""),
	("CXX_LIBS",         ""),

	## Erlang
	("ERL_VERSION",      "16"),
	("EXT_DEPS",         ""),
	("EXT_DEPS_DIR",     "deps"),

	## General
	("INCLUDE_DIRS",     ""),
	("INSTALL_DIR",      "install"),

	("LIB_DIRS",         ""),
	("SRC_DIR",          "src")
]

