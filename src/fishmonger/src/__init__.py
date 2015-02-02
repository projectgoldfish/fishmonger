import fishmonger.config
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
	def configure(self, env_config, app_configs):
		self.getName()

		if not hasattr(self, "defaults"):
			self.defaults = {}

		if not hasattr(self, "extensions"):
			raise ToolChainException("%s MUST define a list of extensions during __init__!" % self.__class__)
		elif not isinstance(self.extensions, list):
			raise ToolChainException("%s MUST define a list of extensions during __init__!" % self.__class__)

		self.env_config  = env_config
		self.tool_config = fishmonger.config.ToolChainConfig(self.getName(), defaults=self.defaults, env_config=self.env_config)

		app_prerequisites         = {}
		self.tc_configs_byAppName = {}
		self.app_configs_byName   = {}
		for config in app_configs:
			if PyFind.findAllByExtensions(self.extensions, config.srcDir(), root_only=True) != []:
				## Update the tool chain config based on this applications specific toolchain config.
				app_tool_config                        = self.tool_config.clone()
				app_tool_config.merge(PyConfig.FileConfig(os.path.join(config.dir, ".fishmonger." + self.getName())))

				self.tc_configs_byAppName[config.name] = fishmonger.config.AppConfig(config.dir, env_config=self.env_config, tool_config=app_tool_config)
				self.app_configs_byName[config.name]   = self.tc_configs_byAppName[config.name]

				app_prerequisites[config.name]         =  self.tc_configs_byAppName[config.name].prerequisiteApps()

		app_order = PyUtil.determinePriority(app_prerequisites)
		self.apps = []
		for app in app_order:
			self.apps.append(self.app_configs_byName[app])

		## Return the list of apps used
		return self.app_configs_byName.keys()

	def runAction(self, action, function):
		for app in self.apps:
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

def addToolChains(array, target, prefix=""):
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







