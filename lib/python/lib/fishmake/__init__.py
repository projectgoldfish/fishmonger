import fishmake.toolchains

import os
import os.path

import pybase.dir as PyDir
import pybase

from pybase.config import GlobalConfig as PyConfig

import pybase.git as PyGit

class AppConfig(object):
	def __init__(self, app, app_dir, app_config):
		self.config    = app_config.clone()
		self.name      = app
		self.app_dir   = app_dir

	def version(self):
		return self.name + "-" + self.config["VERSION"]

	def clone(self):
		return AppConfig(self.name, self.app_dir, self.config)

	def appDir(self):
		return os.path.join(self.config["SRC_DIR"], self.app_dir)

	def buildDir(self):
		return os.path.join(self.appDir(), self.config["BUILD_DIR"])

	def docDir(self):
		return os.path.join(self.appDir(), "doc/")

	def installDir(self, path):
		return os.path.join(self.config["INSTALL_PREFIX"], path, self.version())

	def srcDir(self):
		return os.path.join(self.appDir(), self.config["APP_SRC_DIR"])

class ToolChain(object):
	def __init__():
		pass

	def configure(self, config):
		print self.__class__.__name__, "does not implement configure!"

	def do_configure(self, file, extensions, config, defaults={}):
		tool_config = config.clone()
		tool_config.merge(defaults)
		tool_config.merge(pybase.config.parse(file))

		apps = []
		for app_config in tool_config["APP_CONFIG"]:
			if PyDir.findFilesByExts(extensions, app_config.srcDir()):
				print PyDir.findFilesByExts(extensions, app_config.srcDir()), extensions, app_config.srcDir()
				## Update the tool chain config based on this applications specific config.
				tapp_config = tool_config.clone()
				tapp_config.merge(pybase.config.parseFile(os.path.join(app_config.appDir(), file)))

				## Merge the tool config into the application config
				napp_config = app_config.clone()
				napp_config.config.merge(tapp_config.config)

				apps.append(napp_config)

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
	("APP_SRC_DIR",      "src"),
	
	("VERSION",          PyGit.getVersion()),

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
	("INSTALL_PREFIX",   "install"),

	("LIB_DIRS",         ""),
	("SRC_DIR",          "src"),
	("DOC_DIR",          "doc")
]

def mkNixDirs():
	print "==> Making directories..."
	for nix_dir in fishmake.NIXDirs:
		tnix_dir = PyDir.makeDirAbsolute(os.path.join(PyConfig["INSTALL_PREFIX"], nix_dir))
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
		app_config.append(AppConfig(os.path.basename(app_dir), app_dir, tapp_config))

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






