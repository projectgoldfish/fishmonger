import fishmonger.config
import fishmonger.toolchains

import os
import os.path

import sys

import pybase.config as PyConfig
import pybase.path   as PyPath
import pybase.util   as PyUtil
import pybase.find   as PyFind
import pyrcs         as PyRCS
import pybase.set    as PySet
import pybase.sh     as PySH

import traceback

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
	def uses(self, app_configs):
		self.getName()

		if not hasattr(self, "defaults"):
			self.defaults = {}

		if not hasattr(self, "extensions"):
			raise ToolChainException("%s MUST define a list of extensions during __init__!" % self.__class__)
		elif not isinstance(self.extensions, list):
			raise ToolChainException("%s MUST define a list of extensions during __init__!" % self.__class__)

		apps = []
		for app_config in app_configs:
			print app_config.getName()
			src_files = PyFind.findAllByExtensions(self.extensions, app_config.srcRoot(), root_only=False)
			if src_files != []:
				## Update the tool chain config based on this applications specific toolchain config.				
				apps.append(app_config)
		
		## Return the list of apps used
		return apps

	def runAction(self, app, action, function):
		## No source dirs, nothing to do. Must be built by children

		t_src_dirs = []
		for src_dir in app.src_dirs:
			src_files = PyFind.findAllByExtensions(self.extensions, src_dir, root_only=False)
			if src_files != []:
				t_src_dirs.append(PyPath.makeRelative(src_dir))
		app.src_dirs = t_src_dirs

		if app.src_dirs == []:
			return True

		print "==>", self.getName(), "-", app.getName()

		if not os.path.isdir(app.buildDir()):
			os.makedirs(app.buildDir())
		try:
			cmds = []
			for src_dir in app.src_dirs:
				t_cmds = function(src_dir, app)
				if t_cmds:
					cmds += t_cmds

			if not cmds:
				return True
			for cmd in cmds:
				if hasattr(cmd, "__call__"):
					cmd(app)
				elif isinstance(cmd, basestring):
					if PySH.cmd(cmd, prefix="====>", stdout=True, stderr=True) != 0:
						raise ToolChainException("Failure in %s:%s during: %s" % (action, app, cmd))
				else:
					raise ToolChainException("Invalid %s cmd. Cmds must be string or fun: %s : %s" % (action, app, cmd))

		except Exception as e:
			et, ei, tb = sys.exc_info()
			print "====> Error during", action, "-", e
			for line in traceback.format_tb(tb):
				for t_line in line.strip().split("\n"):
					print "======>", t_line
			 
			return False
		return True

	## Build runs the commands that each app says to use.
	def build(self, app):
		return self.runAction(app, "build", self.buildApp)

	## buildApp is to return a list of strings and functions to call to build the app.
	def buildApp(self, src_dir, app):
		raise ToolChainException("%s MUST implement buildApp or override build!" % self.__class__)

	def install(self, app):
		return self.runAction(app, "install", self.installApp)

	def installApp(self, src_dir, app):
		raise ToolChainException("%s MUST implement installApp or override install!" % self.__class__)

	def document(self, app):
		return self.runAction(app, "document", self.documentApp)

	def documentApp(self, src_dir, app):
		raise ToolChainException("%s MUST implement documentApp or override document!" % self.__class__)

	def generate(self, app):
		return self.runAction(app, "generate", self.generateApp)

	def generateApp(self, src_dir, app):
		raise ToolChainException("%s MUST implement generateApp or override generate!" % self.__class__)

	def link(self, app):
		return self.runAction(app, "link", self.linkApp)

	def linkApp(self, src_dir, app):
		raise ToolChainException("%s MUST implement linkApp or override link!" % self.__class__)

	def getName(self):
		if not hasattr(self, "name"):
			self.name   = self.__module__.split(".")[-1:][0]
		return self.name

	def getApps(self):
		return [app.getName() for app in self.apps]

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







