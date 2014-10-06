import fishmake.toolchains

import os
import os.path

import pybase.config as PyConfig
import pybase.dir    as PyDir
import pybase.git    as PyGit

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

	def name(self):
		return self.name

	def srcDir(self):
		return os.path.join(self.dir, self.config.get("SRC_DIR", "src"))

	def installDir(self, dir=""):
		return os.path.join(self.config.get("INSTALL_PREFIX", "install"), dir)

	def installAppDir(self, dir=""):
		return os.path.join(self.installDir(dir), self.name)

	def installVersionDir(self, dir=""):
		return self.installAppDir(dir) + "-" + PyGit.getVersion()

class ToolChain(object):
	def __init__(self, config={}, defaults={}):
		cli_config  = PyConfig.CLIConfig()
		sys_config  = PyConfig.SysConfig()
		self.config = PyConfig.Config()
		self.config.merge(defaults)
		self.config.merge(sys_config)
		self.config.merge(cli_config)
		self.config.merge(config)

	def configure(self, **kwargs):
		raise Exception("%s does not implement configure!" % self.__class__)

	def doConfigure(self, file=None, extensions=[], defaults={}, app_config=[]):
		self.config.merge(defaults)
		self.config.merge(PyConfig.FileConfig(file))

		apps = []
		for config in app_config:
			if PyDir.findFilesByExts(extensions, config.srcDir()):
				## Update the tool chain config based on this applications specific toolchain config.
				t_config = AppConfig(config.appDir())
				t_config.merge(self.config)
				t_config.merge(PyConfig.FileConfig(os.path.join(config.appDir(), file)))
				apps.append(t_config)

		self.apps = apps
		## If apps is [] we do not need this tool chain
		return apps != []

	def compile(self):
		print self.__class__, "does not implement compile!"
		
	def doc(self):
		print self.__class__, "does not implement doc!"
		
	def install(self):
		print self.__class__, "does not implement install!"

## Fishmake is a special toolchain that calls the other toolchains.
class FishMake(ToolChain):
	## We have to detect the applicaiton folders and generate base app
	## configurations here. Caling doConfigure will fill in the blanks.
	## Once we do that we can setup the tool chains
	def configure(self):
		## Get base config
		self.config.merge(PyConfig.FileConfig(".fishmake"))

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
		self.tool_chains = []
		for tool_chain in fishmake.ToolChains:
			tc = tool_chain.ToolChain(config=self.config)
			if tc.configure(app_config):
				self.tool_chains.append(tc)

	def compile(self):
		print "Compiling"
		## For every available language
		for tool_chain in self.tool_chains:
			tool_chain.compile()
		return 0

	def doc(self):
		print "Generating documentation"
		for tool_chain in self.tool_chains:
			tool_chain.doc()

	def install(self):
		print "Installing"
		print "==> Making directories..."
		for nix_dir in fishmake.NIXDirs:
			tnix_dir = PyDir.makeDirAbsolute(os.path.join(self.config.get("INSTALL_PREFIX", "install"), nix_dir))
			if not os.path.exists(tnix_dir):
				os.makedirs(tnix_dir)
		print "==> Directories made..."
		for tool_chain in self.tool_chains:
			tool_chain.install()

ToolChains = []
for c in fishmake.toolchains.available():
	toolchain = __import__("fishmake.toolchains." + c)
	exec("ToolChains.append(fishmake.toolchains." + c + ")")

## Directories that a built app should contain.
NIXDirs  = ["bin", "doc", "etc", "lib", "sbin", "var", "var/log", "var/run"]








