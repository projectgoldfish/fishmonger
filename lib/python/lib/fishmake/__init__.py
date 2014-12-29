import fishmake.toolchains

import os
import os.path

import pybase.config as PyConfig
import pybase.util   as PyUtil
import pybase.dir    as PyDir
import pybase.rcs    as PyRCS
import pybase.set    as PySet

class AppConfig(PyConfig.Config):
	def __init__(self, dir):
		self.dir     = dir
		self.name    = os.path.basename(dir)
		self.config  = {}
		self.parse()
		pass

	def parse(self):
		pass

	def appDir(self, dir=""):
		if dir == "":
			return self.dir
		else:
			return os.path.join(self.dir, dir)

	def buildDir(self, dir=""):
		build_dir = os.path.join(self.dir, self.config.get("BUILD_DIR", "build"))
		return os.path.join(build_dir, dir)

	def docDir(self, dir=""):
		doc_dir = os.path.join(self.dir, self.config.get("DOC_DIR", "doc"))
		return os.path.join(doc_dir, dir)

	def srcDir(self, dir=""):
		src_dir = os.path.join(self.dir, self.config.get("SRC_DIR", "src"))
		return os.path.join(src_dir, dir)

	def installDir(self, dir=""):
		return os.path.join(self.config.get("INSTALL_PREFIX", "install"), dir)

	def installAppDir(self, dir=""):
		install_app_dir = os.path.join(self.installDir(dir), self.name)
		return install_app_dir + "-" + PyRCS.getVersion()

	def installDocDir(self, dir=""):
		doc_dir = os.path.join(self.installDir("doc"), dir)
		return os.path.join(doc_dir, self.name + "-" + PyRCS.getVersion())

	def prerequisiteApps(self):
		return self.config.get("BUILD_AFTER_APPS", [])

	def prerequisiteTools(self):
		return self.config.get("BUILD_AFTER_TOOLS", [])

class ToolChain(object):
	def __init__(self, config={}, defaults={}):
		cli_config  = PyConfig.CLIConfig()
		sys_config  = PyConfig.SysConfig()
		self.config = PyConfig.Config()
		self.config.merge(defaults)
		self.config.merge(sys_config)
		self.config.merge(cli_config)
		self.config.merge(config)

	## Functions that MUST be implemented
	def configure(self, **kwargs):
		raise Exception("%s does not implement configure!" % self.__class__)

	def buildCommands(self, app):
		raise Exception("%s MUST implement buildCommands or override build!" % self.__class__)

	def installApp(self, app):
		raise Exception("%s MUST implement installApp or override install!" % self.__class__)

	def installDoc(self, app):
		raise Exception("%s MUST implement installDoc or override doc!" % self.__class__)		

	def name(self):
		raise Exceltion("%s is unnamed!", self.__class__)

	## Functions that MAY be implemented, but have default behavior that should be good enough.
	def doConfigure(self, file=None, extensions=[], defaults={}, app_config=[]):
		self.config.merge(defaults)
		self.config.merge(PyConfig.FileConfig(file))

		apps = {}
		for config in app_config:
			if PyDir.findFilesByExts(extensions, config.srcDir()) != []:
				## Update the tool chain config based on this applications specific toolchain config.
				apps[config.name] = AppConfig(config.appDir())
				apps[config.name].merge(self.config)
				apps[config.name].merge(PyConfig.FileConfig(os.path.join(config.appDir(), file)))

		## We need to sort the apps based on what they require
		## Make a dict of app:requirements to make this easier
		requirements = {}
		for app in apps:
			requirements[app] = apps[app].prerequisiteApps()

		self.apps   = []
		build_order = PyUtil.determinePriority(requirements)
		build_order = PyUtil.prioritizeList(apps.keys(), build_order)
		for app in build_order:
			self.apps.append(apps[app])

		## If apps is [] we do not need this tool chain
		return apps != []	

	def build(self):
		for app in self.apps:
			print "====>", app.name
			if not os.path.isdir(app.buildDir()):
				os.mkdir(app.buildDir())
			try:
				cmds = self.buildCommands(app)
				if not cmds:
					continue
				for cmd in cmds:
					if hasattr(cmd, "__call__"):
						cmd(app)
					elif isinstance(cmd, basestring):
						if PyUtil.shell(cmd, prefix="======>", stdout=True, stderr=True) != 0:
							raise Exception("Failure compiling %s during: %s" % (app.name, cmd))
					else:
						raise Exception("Invalid build cmd. Cmds must be string or fun: %s : %s" % (app.name, cmd))

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
		tool_chains = []
		for app in self.apps:
			tool_chains.append(app.prerequisiteTools())
		return PyUtil.mergePrioritizedLists(tool_chains)


def addToolChains(array, target="ToolChains", prefix=""):
	if prefix != "":
		prefix += "."

	modules = []
	for c in array:
		modules.append(prefix + c)
	PyUtil.loadModules(modules, target)

ToolChains = []
Dependents = []

addToolChains(fishmake.toolchains.available(),  ToolChains, "fishmake.toolchains");
addToolChains(fishmake.toolchains.dependable(), Dependents, "fishmake.toolchains");

## Directories that a built app should contain.
NIXDirs  = ["bin", "doc", "etc", "lib", "sbin", "var", "var/log", "var/run"]








