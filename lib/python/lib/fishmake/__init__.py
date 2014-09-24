import fishmake.languages

import os
import os.path

import pybase.dir as PyDir

from pybase.config import GlobalConfig as PyConfig
from fishmake.installer import install   as install

Languages = []
for c in fishmake.languages.available():
	lang = __import__("fishmake.languages." + c)
	exec("Languages.append(lang.languages." + c + ".toolChain())")

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
	("DEP_DIR",          "deps"),
	("DEP_DIRS",         ""),

	## General
	("INCLUDE_DIRS",     ""),
	("INSTALL_DIR",      "install"),

	("LIB_DIRS",         ""),
	("SRC_DIR",          "src")
]

def compile():
	print "Compiling"
	res = 0

	## For every available language
	for language in PyConfig["LANGUAGES"]:
		language.compile()
				
	print "Compilation done"
	return res

def configure():
	PyConfig["SRC_DIR"]      = os.path.join(os.getcwd(),PyConfig["SRC_DIR"])
	PyConfig["DEP_DIR"]      = os.path.join(os.getcwd(),PyConfig["DEP_DIR"])

	PyConfig["APP_DIRS"]     = PyConfig["APP_DIRS"].split(":") + PyDir.getDirDirs(PyConfig["SRC_DIR"])
	PyConfig["LIB_DIRS"]     = PyConfig["LIB_DIRS"].split(":")
	PyConfig["INCLUDE_DIRS"] = PyConfig["INCLUDE_DIRS"].split(":")
	PyConfig["DEP_DIRS"]     = PyConfig["DEP_DIRS"].split(":") + PyDir.getDirDirs(PyConfig["DEP_DIR"])

	## Clear the possible ""
	for arr in ["APP_DIRS", "LIB_DIRS", "INCLUDE_DIRS", "DEP_DIRS"]:
		if "" in PyConfig[arr]:
			PyConfig[arr].remove("")

	## Get the include dirs for this project.
	dirs = PyDir.findDirsByName("include", PyConfig["SRC_DIR"])
	for dir in PyConfig["LIB_DIRS"]:
		dirs += PyDir.findDirsByName("include", dir)
	for dir in PyConfig["DEP_DIRS"]:
		dirs += PyDir.findDirsByName("include", dir)
	PyConfig["INCLUDE_DIRS"] += dirs

	## Configure languages.
	## Determine which we use/dont.
	languages = []
	for language in fishmake.Languages:
		if language.configure(PyConfig):
			languages.append(language)

	PyConfig["LANGUAGES"] = languages

def mkDirs():
		print "====> Making directories..."
		for nix_dir in fishmake.NIXDirs:
			tnix_dir = PyDir.makeDirAbsolute(os.path.join(PyConfig["INSTALL_DIR"], nix_dir))
			if not os.path.exists(tnix_dir):
				os.makedirs(tnix_dir)
		print "====> Directories made..."

def install():
	print "Installing"
	mkDirs()
	for language in PyConfig["LANGUAGES"]:
		language.install()