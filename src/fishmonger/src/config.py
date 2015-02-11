
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

class AppConfigDirTypes:
	base, app = range(2)

class AppToolConfig(PyConfig.Config):
	def __init__(self, dir, *args):
		self.dir          = dir
		self.src_dirs     = []

		self.parent       = None
		self.children     = []

		self.config       = {}

		self.defaults     = {
			"BUILD_AFTER_TOOLS" : PySet.Set(), ## ToolChains that must be run first
			"BUILD_AFTER_APPS"  : PySet.Set(), ## Apps that must be built first
			"BUILD_AFTER"       : PySet.Set(), ## Specific Tool/App pairs that must be run first

			"DEPENDENCIES"      : PySet.Set(), ## Apps in seperate repositories

			"INCLUDE_DIRS"      : PySet.Set(), ## Directories that include files reside in
			"LIB_DIRS"          : PySet.Set(), ## Directories prebuilt libraries exist in

			"DOC_DIR"           : "doc",       ## Directory to install documentation into
			"SRC_DIR"           : "src",       ## Directory to look for source code in

			"BUILD_DIR"         : "build",     ## Directory to place built files into
			"DEP_DIR"           : "deps",      ## Directory to checkout code into

			"INSTALL_PREFIX"    : "install",   ## Directory to install into


			"TOOL_OPTIONS"      : PySet.Set(),
			"APP_OPTIONS"       : PySet.Set()
		}
		
		self.constants    = ["INSTALL_PREFIX"]
		
		self.types        = {
			"INCLUDE_DIRS" : PyConfig.parseDirs,
			"LIB_DIRS"     : PyConfig.parseDirs
		}

		self.allowed      = {x : True for x in self.defaults}

		self.set_behavior = PyConfig.ConfigSetBehavior.write
		self.parse(*args)

	def parse(self, env_config, tool_config, app_config):
		env_defaults  = {
			"DEPENDENCIES"      : PySet.Set(), ## Apps in seperate repositories

			"INCLUDE_DIRS"      : PySet.Set(), ## Directories that include files reside in
			"LIB_DIRS"          : PySet.Set(), ## Directories prebuilt libraries exist in

			"DOC_DIR"           : "doc",       ## Directory to install documentation into
			"SRC_DIR"           : "src",       ## Directory to look for source code in

			"INSTALL_PREFIX"    : "install",   ## Directory to install into

			"DEP_DIR"           : "deps"       ## Directory to checkout code into
		}

		tool_defaults = {
			"BUILD_AFTER_TOOLS" : PySet.Set(), ## ToolChains that must be run first

			"INCLUDE_DIRS"      : PySet.Set(), ## Directories that include files reside in
			"LIB_DIRS"          : PySet.Set(), ## Directories prebuilt libraries exist in

			"DOC_DIR"           : "doc",       ## Directory to install documentation into
			"SRC_DIR"           : "src",       ## Directory to look for source code in
			"BUILD_DIR"         : "build",     ## Directory to place built files into

			"TOOL_OPTIONS"      : PySet.Set()
		}

		app_defaults  = {
			"BUILD_AFTER_APPS"  : PySet.Set(), ## Apps that must be built first
			"BUILD_AFTER"       : PySet.Set(), ## Specific Tool/App pairs that must be run first

			"DEPENDENCIES"      : PySet.Set(), ## Apps in seperate repositories
			
			##
			"INCLUDE_DIRS"      : PySet.Set(), ## Directories that include files reside in
			"LIB_DIRS"          : PySet.Set(), ## Directories prebuilt libraries exist in
			
			"DOC_DIR"           : "doc",       ## Directory to install documentation into
			"SRC_DIR"           : "src",       ## Directory to look for source code in
			"BUILD_DIR"         : "build",     ## Directory to place built files into
			
			"APP_OPTIONS"       : {}           ## Free space. Used by tool chain to 
		}

		env_allowed    = {x : True for x in env_defaults.keys()}
		tool_allowed   = {x : True for x in tool_defaults.keys()}
		app_allowed    = {x : True for x in app_defaults.keys()}

		env_constants  = ["INSTALL_PREFIX"]
		tool_constants = []
		app_constants  = []


		t_env_config   = PyConfig.Config(defaults=env_defaults, allowed=env_allowed, types=self.types, constants=env_constants)
		t_env_config.safeMerge(env_config)

		t_tool_config  = PyConfig.Config(defaults=tool_defaults, allowed=tool_allowed, types=self.types, constants=tool_constants)
		t_tool_config.safeMerge(tool_config)

		t_app_config   = PyConfig.Config(defaults=app_defaults, allowed=app_allowed, types=self.types, constants=app_constants)
		t_app_config.safeMerge(app_config)

		self.safeMerge(t_env_config)
		self.safeMerge(t_tool_config)
		self.safeMerge(t_app_config)
		self.safeMerge(PyConfig.CLIConfig())

	def name(self):
		return os.path.basename(self.dir)

	def root(self):
		return self.dir

	def getDir(self, prefix="", suffix="", base="", version=False, absolute=False, file="", install=False, **kwargs):
		dir = ""
		if install:
			dir = self["INSTALL_PREFIX"]
		else:
			dir = self["SRC_DIR"]

		if version:
			base = base + "-" + PyRCS.getVersion()
 
		dir = os.path.join(dir, os.path.join(prefix, os.path.join(base, os.path.join(suffix, file)))

		if absolute:
			dir = PyPath.makeAbsolute(dir)
		else:
			dir = PyPath.makeRelative(dir)
		return dir
 
 	def srcDir(self):
 		return self.getDir(prefix=self.dir, base=self["SRC_DIR"])

	def buildDir(self):
		return self.getDir(prefix=self.dir, base=self["BUILD_DIR"])

	def installDir(self, install=True, **kwargs):
		return self.getDir(install=True, **kwargs)

	def installEtcDir(self, subdir="", file=""):
		return self.getDir(prefix="etc", base=subdir, file=file, install=True)

	def installBinDir(self, subdir="", file=""):
		return self.getDir(prefix="bin", base=subdir, file=file,  install=True)

	def installLibDir(self, subdir="", file=""):
		return self.getDir(prefix="lib", base=subdir, file=file,  install=True)

	def instalVarDir(self, subdir="", file=""):
		return self.getDir(prefix="var", base=subdir, file=file,  install=True)

	def installLangDir(self, lang, subdir="", file=""):
		return self.getDir(prefix="lib", base=lang + "/lib/" + self.name(), suffix=subdir, file=file, install=True)

class ConfigMap():
	def __init__(*args, **kwargs):
		raise PyConfig.ConfigException("ConfipMaps MUST implement init.")

	def __getitem__(self, key):
		return self.mapping[key].config

	def getNodes(self):
		return self.mapping.keys()		
	
class ConfigTree(ConfigMap):
	def __init__(self, parent=None, file=".fishmonger", dir=".", mapping=None, **kwargs):
		if mapping == None:
			mapping = {}

		self.parent     = parent
		self.dir        = dir

		mapping[dir]    = self
		dir_config      = PyConfig.FileConfig(file=os.path.join(dir, file), **kwargs)
		if parent:
			self.config = parent.config.clone()
			self.config.merge(dir_config)
			
		else:
			self.config = dir_config

		self.children   = [ConfigTree(parent=self, file=file, dir=d, mapping=mapping, **kwargs) for d in PyFind.getDirDirs(dir)]
		self.mapping    = mapping

	def __getitem__(self, key):
		return self.mapping[key].config

	def getNodes(self):
		return self.mapping.keys()

class ConfigPath(ConfigMap):
	def __init__(self, parent=None, file=".fishmonger", root=".", path=".", mapping={}, **kwargs):
		path            = PyPath.makeRelative(path, root)
		self.mapping    = {}

		t_path = ""
		parent = None
		for dir in path.split("/"):
			t_path = os.path.join(t_path, dir)
			dir_config  = PyConfig.FileConfig(os.path.join(t_path, file), **kwargs)

			if parent:
				self.mapping[t_path] = parent.config.clone()
				self.mapping[t_path].merge(dir_config)
			else:
				parent               = dir_config
				self.mapping[t_path] = dir_config

	def __getitem__(self, key):
		return self.mapping[key]
