from pybase.config import Config as PyConfig

import os
import os.path

import pybase.dir as PyDir

import fishmake

def configure():
	PyConfig["SRC_DIR"]      = os.path.join(os.getcwd(),PyConfig["SRC_DIR"])

	PyConfig["APP_DIRS"]     = PyConfig["APP_DIRS"].split(":") + PyDir.getAppDirs(PyConfig["SRC_DIR"])
	PyConfig["LIB_DIRS"]     = PyConfig["LIB_DIRS"].split(":")
	PyConfig["INCLUDE_DIRS"] = PyConfig["INCLUDE_DIRS"].split(":")
	PyConfig["EXT_DEPS"]     = PyConfig["EXT_DEPS"].split(":")

	for arr in ["APP_DIRS", "LIB_DIRS", "INCLUDE_DIRS", "EXT_DEPS"]:
		if "" in PyConfig[arr]:
			PyConfig[arr].remove("")

	if os.path.isdir(PyConfig["EXT_DEPS_DIR"]):
		for dir in os.listdir(PyConfig["EXT_DEPS_DIR"]):
			dir = os.path.join(PyConfig["EXT_DEPS_DIR"], dir)
			if os.path.isdir(dir):
				if not dir in PyConfig["EXT_DEPS"]:
					PyConfig["EXT_DEPS"].append(dir)

	## Get the include dirs for this project.
	dirs = PyDir.findDirsByName("include", PyConfig["SRC_DIR"])
	for dir in PyConfig["LIB_DIRS"]:
		dirs += PyDir.findDirsByName("include", dir)
	for dir in PyConfig["EXT_DEPS"]:
		dirs += PyDir.findDirsByName("include", dir)
	PyConfig["INCLUDE_DIRS"] += dirs

	## Detect languages to use
	languages = {}
	for app_dir in PyConfig["APP_DIRS"]:
		
		types      = []
		tlanguages = []

		src_dir = os.path.join(app_dir, "src")

		for compiler in fishmake.usableLanguages:
			try:
				types = compiler.getFileTypes()
			except:
				types = []
			if PyDir.findFilesByExts(types, src_dir):
				tlanguages.append(compiler)
		languages[app_dir] = tlanguages
	PyConfig["LANGUAGES"] = languages