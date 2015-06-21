import fishmonger.config
import fishmonger.toolchains
import fishmonger.dirflags as DF

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

import pybase.exception as PyExcept

import pybase.log    as PyLog

import traceback

class ToolChainException(PyExcept.BaseException):
	pass

class ToolChain(object):
	## Functions that MUST be implemented
	def __init__(self):
		raise ToolChainException("%s MUST implement init!" % self.__class__)

	## Functions that MAY be implemented, but have default behavior that should be good enough.
	def uses(self, app):
		self.name()

		PyLog.debug("Determining usage", app.path(DF.source|DF.src), log_level=5)

		if not hasattr(self, "defaults"):
			self.defaults = {}

		if not hasattr(self, "extensions"):
			raise ToolChainException("%s MUST define a list of extensions during __init__!" % self.__class__)
		elif not isinstance(self.extensions, list):
			raise ToolChainException("%s MUST define a list of extensions during __init__!" % self.__class__)

		src_configs = []
		for child in [app] + app.children:
			PyLog.debug("Looking in", child.path(DF.source|DF.src), log_level=6)

			src_files = PyFind.findAllByExtensions(self.extensions, child.path(DF.source|DF.src), root_only=False)
			PyLog.debug("Found Files", src_files, log_level=6)
			if len(src_files) != 0:
				## Update the tool chain config based on this applications specific toolchain config.				
				src_configs.append(child)
		
		## Return the list of apps used
		return src_configs

	def runAction(self, app, action, function):
		PyLog.log("%s(%s)" % (self.name(), app.name()))
		PyLog.debug("%s(%s)[%s]" % (self.name(), app.name(), app._dir), log_level=6)

		PyLog.increaseIndent()
	
		try:
			cmds = []
			
			## If no children but we're being built
			## We must just be a shallow app.
			for child in [app] + app.children:
				t_cmds = function(child, app)
				PyLog.debug("Returned", t_cmds, log_level=6)
				if t_cmds:
					cmds += t_cmds
		
			if not cmds:
				PyLog.decreaseIndent()
				return True
			for cmd in cmds:
				if hasattr(cmd, "__call__"):
					cmd(app)
				elif isinstance(cmd, basestring):
					if PySH.cmd(cmd, stdout=True, stderr=True) != 0:
						raise ToolChainException("Failure while performing action", action=action, app=app, cmd=cmd)
				else:
					raise ToolChainException("Invalid %s cmd. Cmds must be string or fun: %s : %s" % (action, app, cmd))

		except PyExcept.BaseException as e:
			PyLog.increaseIndent()
			PyLog.error(e)
			PyLog.decreaseIndent()
			PyLog.decreaseIndent()
			return False
		except Exception as e:
			et, ei, tb = sys.exc_info()
			PyLog.error("Error during %s" % action, exception=str(e))
			PyLog.increaseIndent()
			for line in traceback.format_tb(tb):
				for t_line in line.strip().split("\n"):
					PyLog.error(t_line)
			PyLog.decreaseIndent()
			PyLog.decreaseIndent()
			return False

		PyLog.decreaseIndent()
		return True

	## Build runs the commands that each app says to use.
	def build(self, app):
		return self.runAction(app, "build", self.buildApp)

	## buildApp is to return a list of strings and functions to call to build the app.
	def buildApp(self, child, app):
		raise ToolChainException("%s MUST implement buildApp or override build!" % self.__class__)

	def install(self, app):
		return self.runAction(app, "install", self.installApp)

	def installApp(self, child, app):
		raise ToolChainException("%s MUST implement installApp or override install!" % self.__class__)

	def document(self, app):
		return self.runAction(app, "document", self.documentApp)

	def documentApp(self, child, app):
		raise ToolChainException("%s MUST implement documentApp or override document!" % self.__class__)

	def generate(self, app):
		return self.runAction(app, "generate", self.generateApp)

	def generateApp(self, child, app):
		raise ToolChainException("%s MUST implement generateApp or override generate!" % self.__class__)

	def link(self, app):
		return self.runAction(app, "link", self.linkApp)

	def linkApp(self, child, app):
		raise ToolChainException("%s MUST implement linkApp or override link!" % self.__class__)

	def package(self, app):
		return self.runAction(app, "package", self.packageApp)

	def packageApp(self, child, app):
		raise ToolChainException("%s MUST implement packageApp or override package!" % self.__class__)

	def name(self):
		if not hasattr(self, "tc_name"):
			self.tc_name   = self.__module__.split(".")[-1:][0]
		return self.tc_name

	def getApps(self):
		return [app.name() for app in self.apps]

AllToolChains      = PySet.Set()

InternalToolChains = PySet.Set()
ExternalToolChains = PySet.Set()

GenerateToolChains = PySet.Set()
BuildToolChains    = PySet.Set()
LinkToolChains     = PySet.Set()
DocumentToolChains = PySet.Set()
InstallToolChains  = PySet.Set()
PackageToolChains  = PySet.Set()

def addToolChains(array, target, prefix=""):
	if isinstance(array, basestring):
		array = [array]

	if prefix != "":
		prefix += "."

	modules = []
	for c in array:
		modules.append(prefix + c)
	PyUtil.loadModules(modules, target)
	PyUtil.loadModules(modules, AllToolChains)

def addInternalToolChains(array):
	addToolChains(array, InternalToolChains)
	
def addExternalToolChains(array):
	addToolChains(array, ExternalToolChains)
	
def addGenerateToolChains(array):
	addToolChains(array, GenerateToolChains)

def addBuildToolChains(array):
	addToolChains(array, BuildToolChains)

def addLinkToolChains(array):
	addToolChains(array, LinkToolChains)

def addDocumentToolChains(array):
	addToolChains(array, DocumentToolChains)

def addInstallToolChains(array):
	addToolChains(array, InstallToolChains)

def addPackageToolChains(array):
	addToolChains(array, PackageToolChains)

addToolChains(fishmonger.toolchains.internal(), InternalToolChains, "fishmonger.toolchains");
addToolChains(fishmonger.toolchains.external(), ExternalToolChains, "fishmonger.toolchains");

addToolChains(fishmonger.toolchains.generate(), GenerateToolChains, "fishmonger.toolchains");
addToolChains(fishmonger.toolchains.build(),    BuildToolChains,    "fishmonger.toolchains");
addToolChains(fishmonger.toolchains.link(),     LinkToolChains,     "fishmonger.toolchains");
addToolChains(fishmonger.toolchains.document(), DocumentToolChains, "fishmonger.toolchains");
addToolChains(fishmonger.toolchains.install(),  InstallToolChains,  "fishmonger.toolchains");
addToolChains(fishmonger.toolchains.package(),  PackageToolChains,  "fishmonger.toolchains");







