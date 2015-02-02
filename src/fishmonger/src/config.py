
import pyrcs         as PyRCS
import pybase.config as PyConfig

import pybase.set    as PySet

import pybase.path   as PyPath

import os.path

def dirs(ds):
	t_ds = PySet.Set(ds)
	r_ds = PySet.Set()

	for t_d in t_ds:
		r_ds.append(t_d.split(""))
	return 

class AppConfig(PyConfig.Config):
	def __init__(self, dir, env_config=None, tool_config=None, defaults={}, **kwargs):
		self.dir = dir

		self.env_config  = env_config
		self.tool_config = tool_config
		
		defaults = {
			"BUILD_AFTER_APPS"  : PySet.Set(),
			"DEPENDENCIES"      : PySet.Set(),
			"INCLUDE_DIRS"      : PySet.Set(),
			"LIB_DIRS"          : PySet.Set(),
			"DOC_DIR"           : "doc",
			"SRC_DIR"           : "src",
			"BUILD_DIR"         : "build",
			"INSTALL_PREFIX"    : "install"
		}

		PyConfig.Config.__init__(self, defaults=defaults, **kwargs)
		
	def parse(self):
		if self.dir == ".":
			self.name = os.path.basename(os.getcwd())
		else:
			self.name = os.path.basename(self.dir)

		## Merge in the env config
		if self.env_config:
			self.merge(self.env_config)
		
		## Merge in app specific tool config
		if self.tool_config:
			file_config = PyConfig.FileConfig(os.path.join(self.dir, ".fishmonger." + self.tool_config.tool_chain))
			self.tool_config.merge(file_config)
			self.merge(self.tool_config)

		## Clear out values we will not inherit
		self["DEPENDENCIES"] = self.defaults["DEPENDENCIES"]
		
		## Merge in app specific config
		file_config = PyConfig.FileConfig(os.path.join(self.dir, ".fishmonger.app"))
		self.merge(file_config)

		## Update fields
		for (name, url) in self["DEPENDENCIES"]:
			self["BUILD_AFTER_APPS"].append(name)

	def clone(self):
		copy             = AppConfig(self.dir)
		copy.dir         = self.dir
		copy.name        = self.name
		copy.env_config  = self.env_config
		copy.tool_config = self.tool_config

		print copy.name

		return self.doClone(copy)

	def getDir(self, prefix="", suffix="", root="", version=False, absolute=False, app=False, file="", **kwargs):
		if app:
			root = os.path.join()

		if version:
			root = root + "-" + PyRCS.getVersion()

		dir = os.path.join(prefix, os.path.join(root, os.path.join(suffix, file)))
		if absolute:
			dir = PyPath.makeAbsolute(dir)
		return dir

	def appDir(self, **kwargs):
		return self.getDir(root=self.dir, **kwargs)

	def buildDir(self, dir="", **kwargs):
		return self.getDir(prefix=self.dir,  root=self.get("BUILD_DIR"), suffix=dir, **kwargs)

	def docDir(self, dir=""):
		return self.getDir(prefix=self.dir,  root=self.get("DOC_DIR"),   suffix=dir, **kwargs)

	def srcDir(self, dir="", **kwargs):
		return self.getDir(prefix=self.dir,  root=self.get("SRC_DIR"),   suffix=dir, **kwargs)

	def installDir(self, dir="", prefix="", **kwargs):
		return self.getDir(prefix=self.get("INSTALL_PREFIX"), root=prefix,   suffix=dir, absolute=True, **kwargs)

	def installAppDir(self, dir="", prefix="", **kwargs):
		return self.getDir(prefix=self.get("INSTALL_PREFIX"), root=os.path.join(prefix, self.name), suffix=dir, absolute=True, **kwargs)

	def installDocDir(self, dir="", prefix="", **kwargs):
		return self.getDir(prefix=self.get("INSTALL_PREFIX"), root=dir, suffix=self.name, absolute=True, **kwargs)

	def prerequisiteApps(self):
		return self.get("BUILD_AFTER_APPS")

class ToolChainConfig(PyConfig.Config):
	def __init__(self, tool_chain, env_config=None, defaults={}, allowed=None, suppress_errors=None, **kwargs):
		self.tool_chain = tool_chain

		if env_config:
			self.env_config = env_config.clone()
		else:
			self.env_config = None

		defaults = {
			"BUILD_AFTER_TOOLS" : PySet.Set(),
			"INCLUDE_DIRS"      : PySet.Set(),
			"LIB_DIRS"          : PySet.Set(),
			"OPTIONS"           : PySet.Set()
		}

		allowed = {x : True for x in defaults.keys()}

		PyConfig.Config.__init__(self, defaults=defaults, allowed=allowed, **kwargs)

	def parse(self):
		## Merge in the env config
		if self.env_config :
			self.merge(self.env_config)
		self.merge(PyConfig.FileConfig(".fishmonger." + self.tool_chain))

	def clone(self):
		copy            = ToolChainConfig(self.tool_chain)
		copy.env_config = self.env_config
		return self.doClone(copy)

class EnvConfig(PyConfig.Config):
	def __init__(self, defaults={}, **kwargs):
		defaults = {
			"DEPENDENCIES"      : PySet.Set(),
			"INCLUDE_DIRS"      : PySet.Set(),
			"LIB_DIRS"          : PySet.Set(),
			"DOC_DIR"           : "doc",
			"SRC_DIR"           : "src",
			"BUILD_DIR"         : "build",
			"INSTALL_PREFIX"    : "install",
			"DEP_DIR"           : "deps",
			"SKIP_UPDATE"       : "FALSE"
		}
		PyConfig.Config.__init__(self, defaults=defaults, **kwargs)


	def parse(self):
		self.merge(PyConfig.SysConfig())
		self.merge(PyConfig.FileConfig(".fishmonger"))
		self.merge(PyConfig.CLIConfig())