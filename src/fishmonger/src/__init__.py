import fishmonger.toolchains

import os
import os.path

import pybase.config as PyConfig
import pybase.path   as PyPath
import pybase.util   as PyUtil
import pybase.find   as PyFind
import pyrcs         as PyRCS
import pybase.set    as PySet
import pybase.sh     as PySH


class AppConfig(PyConfig.Config):
	def __init__(self, dir):
		self.dir      = dir
		if dir == ".":
			self.name = os.path.basename(os.getcwd())
		else:
			self.name = os.path.basename(dir)

		self.defaults = {
			"BUILD_AFTER_APPS"  : [],
			"BUILD_DIR"         : "build",
			"DEPENDENCIES"      : [],
			"DOC_DIR"           : "doc",
			"INSTALL_PREFIX"    : "install",
			"SRC_DIR"           : "src"
		}

		self.constants = [
			"INSTALL_PREFIX"
		]

		self.config = {}

		self.merge(PyConfig.FileConfig(os.path.join(dir, ".fishmonger.app")))

		for (name, url) in self.get("DEPENDENCIES"):
			if name not in self.get("BUILD_AFTER_APPS"):
				self.get("BUILD_AFTER_APPS").append(name)

	def appDir(self, dir=""):
		if dir == "":
			return self.dir
		else:
			return os.path.join(self.dir, dir)

	def buildDir(self, dir=""):
		build_dir = os.path.join(self.dir, self.get("BUILD_DIR"))
		return os.path.join(build_dir, dir)

	def docDir(self, dir=""):
		doc_dir = os.path.join(self.dir, self.get("DOC_DIR"))
		return os.path.join(doc_dir, dir)

	def srcDir(self, dir=""):
		src_dir = os.path.join(self.dir, self.get("SRC_DIR"))
		return os.path.join(src_dir, dir)

	def installDir(self, dir=""):
		return PyPath.makeAbsolute(os.path.join(self.get("INSTALL_PREFIX"), dir))

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
		return self.get("BUILD_AFTER_APPS")

class ToolChainException(Exception):
	def __init__(self, value):
		self.value = value
	
	def __str__(self):
		return repr(self.value)

class ToolChain(object):
	## Functions that MUST be implemented
	def __init__(self):
		raise ToolChainException("%s MUST implement init!" % self.__class__)

	## Functions that MAY be implemented, but have default behavior that should be good enough.
	def configure(self, fish_config, app_configs):
	#def configure(self, file=None, extensions=[], defaults={}, app_config=[]):
		self.getName()

		if not hasattr(self, "defaults"):
			self.defaults = {}

		if not hasattr(self, "extensions"):
			raise ToolChainException("%s MUST define a list of extensions during __init__!" % self.__class__)
		elif not isinstance(self.extensions, list):
			raise ToolChainException("%s MUST define a list of extensions during __init__!" % self.__class__)

		self.base_config = fish_config

		self.config = PyConfig.Config(defaults=self.defaults)
		self.config.merge(PyConfig.FileConfig(os.path.join(".", ".fishmonger." + self.name)))

		app_prerequisites         = {}
		self.tc_configs_byAppName = {}
		self.app_configs_byName   = {}
		for config in app_configs:
			if PyFind.findAllByExtensions(self.extensions, config.srcDir(), root_only=True) != []:
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

	def runAction(self, action, function):
		for app in self.apps:
			app_config = {}

			print "====>", app.name
			if not os.path.isdir(app.buildDir()):
				os.makedirs(app.buildDir())
			try:
				cmds = function(app)
				if not cmds:
					continue
				for cmd in cmds:
					if hasattr(cmd, "__call__"):
						cmd(app)
					elif isinstance(cmd, basestring):
						if PySH.cmd(cmd, prefix="======>", stdout=True, stderr=True) != 0:
							raise ToolChainException("Failure in %s:%s during: %s" % (action, app, cmd))
					else:
						raise ToolChainException("Invalid %s cmd. Cmds must be string or fun: %s : %s" % (action, app, cmd))

			except Exception as e:
				print "======> Error during", action, "-", e
				return False
		return True

	## Build runs the commands that each app says to use.
	def build(self):
		return self.runAction("build", self.buildApp)

	## buildApp is to return a list of strings and functions to call to build the app.
	def buildApp(self, app):
		raise ToolChainException("%s MUST implement buildApp or override build!" % self.__class__)

	def install(self):
		return self.runAction("install", self.installApp)

	def installApp(self, app):
		raise ToolChainException("%s MUST implement installApp or override install!" % self.__class__)

	def document(self):
		return self.runAction("document", self.documentApp)

	def documentApp(self, app):
		raise ToolChainException("%s MUST implement documentApp or override document!" % self.__class__)

	def generate(self):
		return self.runAction("generate", self.generateApp)

	def generateApp(self, app):
		raise ToolChainException("%s MUST implement generateApp or override generate!" % self.__class__)

	def link(self):
		return self.runAction("link", self.linkApp)

	def linkApp(self, app):
		raise ToolChainException("%s MUST implement linkApp or override link!" % self.__class__)

	def prerequisiteTools(self):
		## Get the toolchains for the apps, then merge
		## to get the toolchains for this toolchain
		if not hasattr(self, "config"):
			return []
		return self.config.get("BUILD_AFTER_TOOLS", [])

	def prerequisiteToolNames(self):
		## Get the toolchains for the apps, then merge
		## to get the toolchains for this toolchain
		if not hasattr(self, "config"):
			return []

		tool_names = []
		for x in self.config.get("BUILD_AFTER_TOOLS", []):
			if isinstance(x, tuple) and len(x) == 2:
				(x, y) = x
			tool_names.append(x)

		return tool_names

	def getAppConfig(self, app_name):
		config = AppConfig(self.app_configs_byName[app_name].dir)
		config.merge(self.base_config)
		config.merge(self.tc_configs_byAppName[app_name])
		config.merge(self.app_configs_byName[app_name])
		return config

	def getName(self):
		if not hasattr(self, "name"):
			self.name   = self.__module__.split(".")[-1:][0]
		return self.name

AllToolChains      = {}

InternalToolChains = PySet.Set()
ExternalToolChains = PySet.Set()

GenerateToolChains = PySet.Set()
BuildToolChains    = PySet.Set()
LinkToolChains     = PySet.Set()
DocumentToolChains = PySet.Set()
InstallToolChains  = PySet.Set()

def addToolChains(array, target="InternalToolChains", prefix=""):
	if prefix != "":
		prefix += "."

	modules = []
	for c in array:
		modules.append(prefix + c)
	PyUtil.loadModules(modules, target)

	tmp = AllToolChains
	for c in array:
		exec("tmp[\"" + c + "\"] = " + prefix + c)

def addInternalToolChains(array):
	addToolChains(array, AllToolChains)
	addToolChains(array, InternalToolChains)
	
def addExternalToolChains(array):
	addToolChains(array, AllToolChains)
	addToolChains(array, ExternalToolChains)
	
def addGenerateToolChains(array):
	addToolChains(array, AllToolChains)
	addToolChains(array, GenerateToolChains)

def addBuildToolChains(array):
	addToolChains(array, AllToolChains)
	addToolChains(array, BuildToolChains)

def addLinkToolChains(array):
	addToolChains(array, AllToolChains)
	addToolChains(array, LinkToolChains)

def addDocumentToolChains(array):
	addToolChains(array, AllToolChains)
	addToolChains(array, DocumentToolChains)

def addInstallToolChains(array):
	addToolChains(array, AllToolChains)
	addToolChains(array, InstallToolChains)

addToolChains(fishmonger.toolchains.internal(), InternalToolChains, "fishmonger.toolchains");
addToolChains(fishmonger.toolchains.external(), ExternalToolChains, "fishmonger.toolchains");

addToolChains(fishmonger.toolchains.generate(), GenerateToolChains, "fishmonger.toolchains");
addToolChains(fishmonger.toolchains.build(),    BuildToolChains,    "fishmonger.toolchains");
addToolChains(fishmonger.toolchains.link(),     LinkToolChains,     "fishmonger.toolchains");
addToolChains(fishmonger.toolchains.document(), DocumentToolChains, "fishmonger.toolchains");
addToolChains(fishmonger.toolchains.install(),  InstallToolChains,  "fishmonger.toolchains");







