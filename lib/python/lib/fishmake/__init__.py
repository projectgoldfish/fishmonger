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

	def appDir(self):
		return self.dir

	def buildDir(self):
		return os.path.join(self.dir, self.config.get("BUILD_DIR", "build"))

	def srcDir(self):
		return os.path.join(self.dir, self.config.get("SRC_DIR", "src"))

	def installDir(self, dir=""):
		return os.path.join(self.config.get("INSTALL_PREFIX", "install"), dir)

	def installAppDir(self, dir=""):
		return os.path.join(self.installDir(dir), self.name)

	def installVersionDir(self, dir=""):
		return self.installAppDir(dir) + "-" + PyRCS.getVersion()

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

	def name(self):
		raise Exceltion("%s is unnamed!", self.__class__)

	## Functions that MAY be implemented, but have default behavior that should be good enough.
	def doConfigure(self, file=None, extensions=[], defaults={}, app_config=[]):
		self.config.merge(defaults)
		self.config.merge(PyConfig.FileConfig(file))

		apps = {}
		for config in app_config:
			if PyDir.findFilesByExts(extensions, config.srcDir()):
				## Update the tool chain config based on this applications specific toolchain config.
				t_config = AppConfig(config.appDir())
				t_config.merge(self.config)
				t_config.merge(PyConfig.FileConfig(os.path.join(config.appDir(), file)))
				apps[t_config.name] = t_config

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
					if PyUtil.shell(cmd, prefix="======>", stdout=True, stderr=True) != 0:
						raise Exception("Failure compiling %s during: %s" % (app.name, cmd))

			except Exception as e:
				print "======> Error compiling:", e
				return False
		return True		
		
	def install(self):
		for app in self.apps:
			print "====>", app.name
			self.installApp(app)

	def prerequisiteTools(self):
		## Get the toolchains for the apps, then merge
		## to get the toolchains for this toolchain
		tool_chains = []
		for app in self.apps:
			tool_chains.append(app.prerequisiteTools())
		return PyUtil.mergePrioritizedLists(tool_chains)


## Fishmake is a special toolchain that calls the other toolchains.
class FishMake(ToolChain):
	## We have to detect the applicaiton folders and generate base app
	## configurations here. Caling doConfigure will fill in the blanks.
	## Once we do that we can setup the tool chains
	def configure(self, app_config={}):
		print "Configuring"
		## Get base config
		self.config.merge(PyConfig.FileConfig(".fishmake"))

		## Make certain dependencies are up to date
		dependencies = []
		for (target, url) in self.config.get("DEPENDENCIES", []):
			target_dir = os.path.join(self.config["DEP_DIR"], target)
			if not os.path.isdir(target_dir):
				PyRCS.clone(url, target_dir)
			t_appconfig = AppConfig(target_dir)
			t_appconfig.merge(self.config)
			dependencies.append(t_appconfig)

		self.dependents = []
		for tool_chain in fishmake.Dependents:
			tc = tool_chain.ToolChain(config=self.config)
			print "==>", tc.name()
			if tc.configure(dependencies):
				self.dependents.append(tc)

		## Process the base config
		self.config["INCLUDE_DIRS"] = self.config.getDirs("INCLUDE_DIRS") + PyDir.findDirsByName("include")
		self.config["LIB_DIRS"]     = self.config.getDirs("LIB_DIRS")     + PyDir.findDirsByName("lib")
		
		app_dirs = self.config.getDirs("APP_DIRS") + PyDir.getDirDirs(self.config["SRC_DIR"])
		                       
		## We have the app dirs.
		app_config = []
		for app_dir in app_dirs:
			## Make an AppConfig for this appdir
			tconfig = AppConfig(app_dir)
			tconfig.merge(self.config)

			## Update it with any .fishmake in it's directory.
			tconfig.merge(PyConfig.FileConfig(os.path.join(app_dir, ".fishmake")))
			
			## We've made base app config
			app_config.append(tconfig)

		## Configure tool_chains.
		## Determine which we use/dont.
		tool_chains         = {}
		tool_chain_prereqs  = {}
		for tool_chain in fishmake.ToolChains:
			tc = tool_chain.ToolChain(config=self.config)
			print "==>", tc.name()
			if tc.configure(app_config):
				tool_chains[tc.name()]         = tc
				tool_chain_prereqs[tc.name()]  = tc.prerequisiteTools()

		## Get priority list
		tool_chain_order = PyUtil.mergePrioritizedLists(tool_chain_prereqs.values())

		## Make certain all elements are in priority list
		tool_chain_order = PyUtil.prioritizeList(tool_chains.keys(), tool_chain_order)
		
		self.tool_chains = []
		for tool_chain in tool_chain_order:
			self.tool_chains.append(tool_chains[tool_chain])

	def build(self):
		print "Building"
		for tool_chain in self.dependents + self.tool_chains:
			print "==>", tool_chain.name()
			tool_chain.build()

	def install(self, app=None):
		print "Installing"
		for nix_dir in fishmake.NIXDirs:
			tnix_dir = PyDir.makeDirAbsolute(os.path.join(self.config.get("INSTALL_PREFIX", "install"), nix_dir))
			if not os.path.exists(tnix_dir):
				os.makedirs(tnix_dir)
		for tool_chain in self.dependents + self.tool_chains:
			print "==>", tool_chain.name()
			tool_chain.install()

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








