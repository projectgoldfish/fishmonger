
import pyrcs         as PyRCS
import pybase.config as PyConfig

import pybase.set    as PySet

import pybase.path   as PyPath
import pybase.find   as PyFind

import os.path

def dirs(ds):
	t_ds = PySet.Set(ds)
	r_ds = PySet.Set()

	for t_d in t_ds:
		r_ds.append(t_d.split(""))
	return 

class AppConfig(PyConfig.Config):
	def __init__(self, dir, env_config, tool_config, app_config):
		self.dir = dir

		self.parent      = None
		self.src_dirs    = []
			
		self.env_config  = env_config
		self.tool_config = tool_config
		self.app_config  = app_config

		defaults = {
			"BUILD_AFTER_TOOLS" : PySet.Set(),
			"BUILD_AFTER_APPS"  : PySet.Set(),
			"BUILD_AFTER"       : PySet.Set(),
			"DEPENDENCIES"      : PySet.Set(),
			"INCLUDE_DIRS"      : PySet.Set(),
			"LIB_DIRS"          : PySet.Set(),
			"DOC_DIR"           : "doc",
			"SRC_DIR"           : "src",
			"BUILD_DIR"         : "build",
			"INSTALL_PREFIX"    : "install"
		}

		PyConfig.Config.__init__(self, defaults=defaults)
		
	def parse(self):
		if self.dir         == None and \
		   self.env_config  == None and \
		   self.tool_config == None and \
		   self.app_config  == None:
			return

		if self.dir == ".":
			self.name = os.path.basename(os.getcwd())
		else:
			self.name = os.path.basename(self.dir)

		## Merge in the env config
		self.merge(self.env_config)
		## Merge in the tool config
		self.merge(self.tool_config)

		print "???", self.dir, self["DEPENDENCIES"], self.app_config.config

		## Clear out values we will not inherit
		self["DEPENDENCIES"] = self.defaults["DEPENDENCIES"]

		## Merge in the app config
		self.merge(self.app_config)

		## Remerge in CLI Config as that overrides all
		self.merge(PyConfig.CLIConfig())

		## Update fields
		for (name, url) in self["DEPENDENCIES"]:
			self["BUILD_AFTER_APPS"].append(name)

		self.env_config  = None
		self.tool_config = None
		self.app_config  = None

	def clone(self):
		copy             = AppConfig(None, None, None,)
		copy.dir         = self.dir
		copy.name        = self.name
		
		return self.doClone(copy)

	def getName(self):
		return self.name

	def getDir(self, prefix="", suffix="", root="", version=False, absolute=False, app=False, file="", offset=None, **kwargs):
		if app:
			root = os.path.join()

		if version:
			root = root + "-" + PyRCS.getVersion()

		dir = os.path.join(prefix, os.path.join(root, os.path.join(suffix, file)))

		if offset:
			offset = offset[len(self.srcRoot())+1:]
			dir = os.path.join(dir, offset)

		if absolute:
			dir = PyPath.makeAbsolute(dir)
		else:
			dir = PyPath.makeRelative(dir)

		return dir

	def appDir(self, **kwargs):
		return self.getDir(root=self.dir, **kwargs)

	def buildDir(self, dir="", **kwargs):
		return self.getDir(prefix=self.dir,  root=self.get("BUILD_DIR"), suffix=dir, **kwargs)

	def docDir(self, dir=""):
		return self.getDir(prefix=self.dir,  root=self.get("DOC_DIR"),   suffix=dir, **kwargs)

	def srcRoot(self, dir="", **kwargs):
		## If an app_dir/SRC_DIR exists that is the SRC_DIR
		## otherwise app_dir is the SRC_DIR
		dir = self.getDir(prefix=self.dir,  root=self.get("SRC_DIR"),   suffix=dir, **kwargs)
		if os.path.isdir(dir):
			return dir
		else:
			return self.dir

	def installDir(self, dir="", prefix="", **kwargs):
		return self.getDir(prefix=self.get("INSTALL_PREFIX"), root=prefix,   suffix=dir, absolute=True, **kwargs)

	def installAppDir(self, dir="", prefix="", **kwargs):
		return self.getDir(prefix=self.get("INSTALL_PREFIX"), root=os.path.join(prefix, self.name), suffix=dir, absolute=True, **kwargs)

	def installDocDir(self, dir="", prefix="", **kwargs):
		return self.getDir(prefix=self.get("INSTALL_PREFIX"), root=dir, suffix=self.name, absolute=True, **kwargs)

	def getPrerequisites(self):
		## Return a list of tuples
		## [((ToolChain, App), [(ToolChain, App)])]
		## Where each pair MUST be run before this one.

		pre_reqs = []
		for tool in self["BUILD_AFTER_TOOLS"]:
			pre_reqs.append((tool, None))
		for app in self["BUILD_AFTER_APPS"]:
			pre_reqs.append((tool, None))

		return pre_reqs + self["BUILD_AFTER"]

class ToolChainConfig(PyConfig.Config):
	def __init__(self, tool_chain, values, env_config):
		self.tool_chain = tool_chain

		self.env_config = env_config
		self.values     = values

		defaults = {
			"BUILD_AFTER_TOOLS" : PySet.Set(),
			"INCLUDE_DIRS"      : PySet.Set(),
			"LIB_DIRS"          : PySet.Set(),
			"OPTIONS"           : PySet.Set()
		}

		allowed = {x : True for x in defaults.keys()}

		PyConfig.Config.__init__(self, defaults=defaults, allowed=allowed)

	def parse(self):
		if self.tool_chain == None and self.env_config == None and self.values == None:
			return

		## Merge in the env config
		self.merge(self.env_config)
		self.merge(self.values)

		## Remerge in CLI Config as that overrides all
		self.merge(PyConfig.CLIConfig())


		self.env_config = None
		self.values     = None

	def clone(self):
		copy            = ToolChainConfig(None, None, None)
		copy.tool_chain = self.tool_chain

		return self.doClone(copy)

class EnvConfig(PyConfig.Config):
	def __init__(self, values):
		self.values = values
		defaults    = {
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
		PyConfig.Config.__init__(self, defaults=defaults)

	def parse(self):
		self.merge(PyConfig.SysConfig())
		self.merge(self.values)		
		self.merge(PyConfig.CLIConfig())
		self.values = None

class ConfigTree():
	def __init__(self, parent=None, file=".fishmonger", dir=".", mapping={}):
		self.parent     = parent

		self.dir        = dir

		mapping[dir]    = self

		print "File", os.path.join(dir, file)

		dir_config      = PyConfig.FileConfig(os.path.join(dir, file))
		print "\tDIR", dir_config.config

		if parent:
			self.config = parent.config.clone()
			self.config.merge(dir_config)

			print "\t\tMerged", self.config.config
		else:
			self.config = dir_config

		self.children   = [ConfigTree(parent=self, file=file, dir=d, mapping=mapping) for d in PyFind.getDirDirs(dir)]
		self.mapping    = mapping

	def __getitem__(self, key):
		return self.mapping[key]

	def __str__(self):
		print  "\n----\n"
		print "Node " + self.dir
		for c in self.children:
			print "\tChild", c.dir

		print "CONF", self.config.config
		
		for c in self.children:
			print c
		return ""
		

	def getNodes(self):
		return self.mapping.keys()


