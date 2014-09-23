from pybase.config import GlobalConfig as PyConfig

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

	## Detect which apps need which langauges
	languages = {}
	for language in fishmake.usableLanguages:
		apps    = []
		for app_dir in PyConfig["APP_DIRS"]:
			src_dir = os.path.join(app_dir, "src")
			try:
				types = language.getFileTypes()
			except:
				types = []
			if PyDir.findFilesByExts(types, src_dir):
				apps.append(app_dir)
		languages[language] = apps
	PyConfig["LANGUAGES"] = languages