import fishmake.toolchains

import os
import os.path

import pybase.dir as PyDir
import pybase

from pybase.config import GlobalConfig as PyConfig

import pybase.git as PyGit

class ToolChain(object):
	def __init__():
		pass

	def configure(self, config):
		print self.__class__.__name__, "does not implement configure!"

	def do_configure(self, file, extensions, config, defaults={}):
		tool_config = config.clone()
		tool_config.merge(defaults)
		tool_config.merge(pybase.config.parse(file, {"EXECUTABLE" : False, "INSTALL_DOC" : True}))

		apps = []
		for app, app_dir, app_config in tool_config["APP_CONFIG"]:
			src_dir = os.path.join(os.path.join(tool_config["SRC_DIR"], app_dir), app_config["APP_SRC_DIR"])
			if PyDir.findFilesByExts(extensions, src_dir):
				print PyDir.findFilesByExts(extensions, src_dir), extensions, src_dir
				## Update the tool chain config based on this applications specific config.
				tapp_config = tool_config.clone()
				tapp_config.merge(pybase.config.parseFile(os.path.join(app_dir, file)))

				## Merge the tool config into the application config
				napp_config = app_config.clone()
				napp_config.merge(tapp_config.config)

				napp_config["BUILD_DIR"] = os.path.join(os.path.join(tool_config["SRC_DIR"], app_dir), napp_config["BUILD_DIR"])

				apps.append((app, app_dir, napp_config))

		tool_config["APP_CONFIG"] = apps
		self.config = tool_config
		## If apps is [] we do not need this tool chain
		return apps != []

	def compile(self):
		print self.__class__.__name__, "does not implement compile!"
		
	def doc(self):
		print self.__class__.__name__, "does not implement doc!"
		
	def install(self):
		print self.__class__.__name__, "does not implement install!"

ToolChains = []
for c in fishmake.toolchains.available():
	print c
	toolchain = __import__("fishmake.toolchains." + c)
	exec("ToolChains.append(fishmake.toolchains." + c + ".ToolChain())")

## Directories that a built app should contain.
NIXDirs  = ["bin", "doc", "etc", "lib", "sbin", "var", "var/log", "var/run"]

## Initialize config
Defaults = [
	("APP_ID",           PyGit.getId()),
	("APP_DIRS",         ""),
	("APP_MAIN",         False),
	("APP_NAME",         False),
	("APP_COOKIE",       "snickerdoodle"),
	("APP_VERSION",      PyGit.getVersion()),
	("APP_SRC_DIR",      "src"),
	
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
	("BUILD_DIR",        "build"),

	("INCLUDE_DIRS",     ""),
	("INSTALL_DIR",      "install"),

	("LIB_DIRS",         ""),
	("SRC_DIR",          "src")
]

def mkNixDirs():
	print "==> Making directories..."
	for nix_dir in fishmake.NIXDirs:
		tnix_dir = PyDir.makeDirAbsolute(os.path.join(PyConfig["INSTALL_DIR"], nix_dir))
		if not os.path.exists(tnix_dir):
			os.makedirs(tnix_dir)
	print "==> Directories made..."

def compile():
	print "Compiling"
	res = 0

	## For every available language
	for tool_chain in PyConfig["TOOL_CHAINS"]:
		tool_chain.compile()
				
	print "Compilation done"
	return res

def configure():
	PyConfig["SRC_DIR"]      = os.path.join(os.getcwd(),PyConfig["SRC_DIR"])
	PyConfig["DEP_DIR"]      = os.path.join(os.getcwd(),PyConfig["DEP_DIR"])

	PyConfig["LIB_DIRS"]     = PyConfig["LIB_DIRS"].split(":")
	PyConfig["INCLUDE_DIRS"] = PyConfig["INCLUDE_DIRS"].split(":")
	PyConfig["DEP_DIRS"]     = PyConfig["DEP_DIRS"].split(":") + PyDir.getDirDirs(PyConfig["DEP_DIR"])

	PyConfig["APP_DIRS"]     = PyConfig["APP_DIRS"].split(":") + PyDir.getDirDirs(PyConfig["SRC_DIR"])

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

	app_config = []
	for app_dir in PyConfig["APP_DIRS"]:
		tapp_config = PyConfig.clone()
		tapp_config.merge(pybase.config.parseFile(os.path.join(app_dir, ".fishmake")))
		app_config.append((os.path.basename(app_dir), app_dir, tapp_config))

	PyConfig["APP_CONFIG"] = app_config

	## Configure tool_chains.
	## Determine which we use/dont.
	tool_chains = []
	for tool_chain in fishmake.ToolChains:
		if tool_chain.configure(PyConfig):
			tool_chains.append(tool_chain)

	PyConfig["TOOL_CHAINS"] = tool_chains

def install():
	print "Installing"
	mkNixDirs()
	for tool_chain in PyConfig["TOOL_CHAINS"]:
		tool_chain.install()

def doc():
	for tool_chain in PyConfig["TOOL_CHAINS"]:
		tool_chain.doc()






