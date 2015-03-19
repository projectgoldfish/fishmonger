
import pyrcs         as PyRCS
import pybase.config as PyConfig

import pybase.set    as PySet

import pybase.path   as PyPath
import pybase.find   as PyFind

import pybase.kwargs as PyKWArgs

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
		self.src_root     = dir
		self.app_root     = dir
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

			"TOOL_OPTIONS"      : {},
			"TOOL_CLI_OPTIONS"  : PySet.Set(),

			"APP_OPTIONS"       : {},

			## MISC
			"SKIP_UPDATE"       : False
		}
		
		self.constants    = ["INSTALL_PREFIX"]
		
		self.types        = {
			"INCLUDE_DIRS" : PyConfig.parseDirs,
			"LIB_DIRS"     : PyConfig.parseDirs,
			"SKIP_UPDATE"  : bool
		}

		self.allowed      = {x : True for x in self.defaults}

		self.set_behavior = PyConfig.ConfigSetBehavior.merge
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

			"TOOL_CLI_OPTIONS"  : PySet.Set(),

			"TOOL_OPTIONS"      : {}
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
		if tool_config != None:
			t_tool_config.safeMerge(tool_config)
		
		t_app_config   = PyConfig.Config(defaults=app_defaults, allowed=app_allowed, types=self.types, constants=app_constants)
		if app_config != None:
			t_app_config.safeMerge(app_config)
		
		self.safeMerge(t_env_config)
		self.safeMerge(t_tool_config)
		self.safeMerge(t_app_config)
		self.safeMerge(PyConfig.CLIConfig())

	def mergeIfNull(self, values):
		for key in values:
			if key not in self.config:
				self.config[key] = values[key]
			elif isinstance(self.config[key], dict) and isinstance(values[key], dict):
				PyUtil.mergeDicts(self.config[key], values[key])

	def isRoot(self):
		return self.src_root == self.dir

	def offset(self):
		if len(self.src_root) < len(self.dir):
			return self.dir[len(self.src_root)+1:]
		else:
			return ""

	def name(self):
		name = os.path.basename(self.src_root)
		if name == self["SRC_DIR"]:
			return os.path.basename(os.path.dirname(self.src_root))
		if name == ".":
			return os.path.basename(PyPath.makeAbsolute(self.src_root))
		return name

	def root(self):
		return self.dir

	def getDir(self, prefix="", base="", suffix="", file="", version=False, absolute=False, install=False):
		dir = ""
		if install:
			dir = self["INSTALL_PREFIX"]
		
		if version:
			base = base + "-" + PyRCS.getVersion()
 
		dir = os.path.join(dir, os.path.join(prefix, os.path.join(base, os.path.join(self.offset(), os.path.join(suffix, file)))))

		if absolute == True:
			dir = PyPath.makeAbsolute(dir)
		else:
			dir = PyPath.makeRelative(dir)

		return dir
 
	def appDir(self, subdir="", file=""):
		return os.path.join(os.path.join(self.dir, subdir), file)

 	def srcDir(self, subdir="", file=""):
 		src_dir = os.path.join(self.dir, self["SRC_DIR"])
 		if os.path.isdir(src_dir):
 			return os.path.join(os.path.join(src_dir, subdir), file)
 		else:
 			return os.path.join(os.path.join(self.dir, subdir), file)

	def buildDir(self, subdir="", file="", absolute=False):
		path = os.path.join(os.path.join(os.path.join(self.app_root, self["BUILD_DIR"]), subdir), file)
		if absolute:
			path = PyPath.makeAbsolute(path)
		return path
 		
	def installDir(self, install=True, **kwargs):
		args = ["prefix", "base", "suffix", "file", "absolute"]
		return self.getDir(install=True, **PyKWArgs.sanitize(args, **kwargs))

	def installEtcDir(self, subdir="", file="", **kwargs):
		args = ["absolute"]
		return self.getDir(prefix="etc", base=subdir, file=file, install=True, **PyKWArgs.sanitize(args, **kwargs))

	def installBinDir(self, subdir="", file="", **kwargs):
		args = ["absolute"]
		return self.getDir(prefix="bin", base=subdir, file=file,  install=True, **PyKWArgs.sanitize(args, **kwargs))

	def installLibDir(self, subdir="", file="", **kwargs):
		args = ["absolute"]
		return self.getDir(prefix="lib", base=subdir, file=file,  install=True, **PyKWArgs.sanitize(args, **kwargs))

	def installVarDir(self, subdir="", file="", **kwargs):
		args = ["absolute"]
		return self.getDir(prefix="var", base=subdir, file=file,  install=True, **PyKWArgs.sanitize(args, **kwargs))

	def installLangSubDir(self, lang, subdir="", file="", app=False, **kwargs):
		name = self.name()
		if not app:
			name = ""

		args = ["version", "absolute"]
		return self.getDir(prefix="lib", base=lang + "/lib/" + name, suffix=subdir, file=file, install=False, **PyKWArgs.sanitize(args, **kwargs))

	def installLangDir(self, lang, subdir="", file="", app=False, **kwargs):
		name = self.name()
		if not app:
			name = ""

		args = ["version", "absolute"]
		return self.getDir(prefix="lib", base=lang + "/lib/" + name, suffix=subdir, file=file, install=True, **PyKWArgs.sanitize(args, **kwargs))

	def installDocDir(self, lang, subdir="", file="", app=None, version=True, **kwargs):
		args = ["absolute"]
		return self.getDir(prefix="doc/" + lang, base=self.name(), install=True, version=version, **PyKWArgs.sanitize(args, **kwargs))

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
