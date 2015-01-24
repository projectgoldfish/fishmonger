import fishmonger.toolchains

import os
import os.path

import pybase.config as PyConfig
import pybase.path   as PyPath
import pybase.util   as PyUtil
import pybase.dir    as PyDir
import pyrcs         as PyRCS
import pybase.set    as PySet


class AppConfig(PyConfig.Config):
	def __init__(self, dir):
		self.dir      = dir
		if dir == ".":
			self.name = os.path.basename(os.getcwd())
		else:
			self.name = os.path.basename(dir)

		self.config   = {
			"BUILD_AFTER_APPS"  : [],
			"BUILD_DIR"         : "build",
			"DEPENDENCIES"      : [],
			"DOC_DIR"           : "doc",
			"INSTALL_PREFIX"    : "install",
			"SRC_DIR"           : "src"
		}
		self.merge(PyConfig.FileConfig(os.path.join(dir, ".fishmonger.app")))

		for (name, url) in self.config["DEPENDENCIES"]:
			if name not in self.config["BUILD_AFTER_APPS"]:
				self.config["BUILD_AFTER_APPS"].append(name)

	def appDir(self, dir=""):
		if dir == "":
			return self.dir
		else:
			return os.path.join(self.dir, dir)

	def buildDir(self, dir=""):
		build_dir = os.path.join(self.dir, self.config["BUILD_DIR"])
		return os.path.join(build_dir, dir)

	def docDir(self, dir=""):
		doc_dir = os.path.join(self.dir, self.config["DOC_DIR"])
		return os.path.join(doc_dir, dir)

	def srcDir(self, dir=""):
		src_dir = os.path.join(self.dir, self.config["SRC_DIR"])
		return os.path.join(src_dir, dir)

	def installDir(self, dir=""):
		return PyDir.makeDirAbsolute(os.path.join(self.config["INSTALL_PREFIX"], dir))

	def installAppDir(self, dir="", version=True):
		install_app_dir = os.path.join(self.installDir(dir), self.name)
		if version:
			return install_app_dir + "-" + PyRCS.getVersion()
		else:
			return install_app_dir

	def installDocDir(self, dir="", version=True):
		doc_dir = os.path.join(self.installDir("doc"), dir)

		if version:
			return os.path.join(doc_dir, self.name + "-" + PyRCS.getVersion())
		else:
			return os.path.join(doc_dir, self.name)

	def prerequisiteApps(self):
		return self.config["BUILD_AFTER_APPS"]

class ToolChain(object):
	## Functions that MUST be implemented
	def __init__(self):
		raise Exception("%s MUST implement init!" % self.__class__)

	def buildCommands(self, app):
		raise Exception("%s MUST implement buildCommands or override build!" % self.__class__)

	def installApp(self, app):
		raise Exception("%s MUST implement installApp or override install!" % self.__class__)

	def installDoc(self, app):
		raise Exception("%s MUST implement installDoc or override doc!" % self.__class__)

	## Functions that MAY be implemented, but have default behavior that should be good enough.
	def configure(self, fish_config, app_configs):
	#def configure(self, file=None, extensions=[], defaults={}, app_config=[]):
		self.getName()

		if not hasattr(self, "defaults"):
			self.defaults = {}

		if not hasattr(self, "extensions"):
			raise Exception("%s MUST define a list of extensions during __init__!" % self.__class__)
		elif not isinstance(self.extensions, list):
			raise Exception("%s MUST define a list of extensions during __init__!" % self.__class__)

		self.base_config = fish_config

		self.config = PyConfig.Config()
		self.config.merge(self.defaults)
		self.config.merge(PyConfig.FileConfig(os.path.join(".", ".fishmonger." + self.name)))

		app_prerequisites         = {}
		self.tc_configs_byAppName = {}
		self.app_configs_byName   = {}
		for config in app_configs:
			if PyDir.findAllByExtensions(self.extensions, config.srcDir(), root_only=True) != []:
				## Update the tool chain config based on this applications specific toolchain config.
				self.tc_configs_byAppName[config.name] = self.config.clone()
				self.tc_configs_byAppName[config.name].merge(PyConfig.FileConfig(os.path.join(config.appDir(), ".fishmonger." + self.name)))

				self.app_configs_byName[config.name] = config

				app_prerequisites[config.name] = config.prerequisiteApps()

		app_order = PyUtil.determinePriority(app_prerequisites)
		self.apps = []
		for app in app_order:
			if app in self.app_configs_byName:
				self.apps.append(self.getAppConfig(app))

		## Return the list of apps used
		return self.app_configs_byName.keys()

	def build(self):
		for app in self.apps:
			app_config = {}

			print "====>", app.name
			if not os.path.isdir(app.buildDir()):
				os.makedirs(app.buildDir())
			try:
				cmds = self.buildCommands(app)
				if not cmds:
					continue
				for cmd in cmds:
					if hasattr(cmd, "__call__"):
						cmd(app)
					elif isinstance(cmd, basestring):
						if PyUtil.shell(cmd, prefix="======>", stdout=True, stderr=True) != 0:
							raise Exception("Failure compiling %s during: %s" % (app, cmd))
					else:
						raise Exception("Invalid build cmd. Cmds must be string or fun: %s : %s" % (app, cmd))

			except Exception as e:
				print "======> Error compiling:", e
				return False
		return True		
		
	def install(self):
		for app in self.apps:
			print "====>", app.name
			self.installApp(app)

	def doc(self):
		for app in self.apps:
			print "====>", app.name
			self.installDoc(app)

	def prerequisiteTools(self):
		## Get the toolchains for the apps, then merge
		## to get the toolchains for this toolchain
		if not hasattr(self, "config"):
			return []
		return self.config.get("BUILD_AFTER_TOOLS", [])

	def getAppConfig(self, app_name):
		config = AppConfig(self.app_configs_byName[app_name].dir)
		config.merge(self.base_config)
		config.merge(self.tc_configs_byAppName[app_name])
		config.merge(self.app_configs_byName[app_name])
		return config

	def getName(self):
		if not hasattr(self, "name"):
			self.name   = self.__module__.split(".")[-1:][0]
		return self.name;

def addInternalToolChains(array):
	addToolChains(array, InternalToolChains)

def addExternalToolChains(array):
	addToolChains(array, ExternalToolChains)	

def addToolChains(array, target="InternalToolChains", prefix=""):
	if prefix != "":
		prefix += "."

	modules = []
	for c in array:
		modules.append(prefix + c)
	PyUtil.loadModules(modules, target)

InternalToolChains = []
ExternalToolChains = []

addToolChains(fishmonger.toolchains.internal(), InternalToolChains, "fishmonger.toolchains");
addToolChains(fishmonger.toolchains.external(), ExternalToolChains, "fishmonger.toolchains");

## Directories that a built app should contain.
NIXDirs  = ["bin", "doc", "etc", "lib", "sbin", "var", "var/log", "var/run"]








