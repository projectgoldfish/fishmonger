## Python modules included
import os
import sys

## PyBase modules included
import pybase.log       as PyLog
import pybase.find      as PyFind

## Fishmonger modules included
import fishmonger.exceptions as FishExc
import fishmonger.toolchains as FishTC

Stages = [
	"clean",
	"generate",
	"build",
	"link",
	"install",
	"document",
	"package",
	"publish"
]

StageSynonyms = {
	"clean"    : set(["clean"]),
	"generate" : set(["generate"]),
	"build"    : set(["build", "compile"]),
	"link"     : set(["link"]),
	"install"  : set(["install"]),
	"document" : set(["document", "doc"]),
	"package"  : set(["package"]),
	"publish"  : set(["publish"])
}

def getAppDirs(root = "."):
	"""
	getAppDirs(string()::Root) -> [string()]::Return

	Scans the directory structure to determine the application directories.

	Root   - The Directory to start scanning from.

	Return - A list of directories that are root directories for applications
	"""

	def scanSrcDirs(parent=None, root=".", app_dirs=None):
		"""
		scanSrcDirs(string()::Parent, string()::Root, [()]|None::AppDirs) ->

		Scans the directory structure for src directories and thier parents.
		"""
		if app_dirs == None:
			app_dirs = []

		app_dirs.append((parent, root))
		src_dir   = os.path.join(root, "src")
		
		nparent = root
		dirs    = []
		if os.path.isdir(src_dir):
			dirs = PyFind.getDirDirs(src_dir)
		else:
			nparent = parent
			dirs    = PyFind.getDirDirs(root)

		for d in dirs:
			if os.path.basename(d)[0] != ".":
				scanSrcDirs(nparent, d, app_dirs)

		return app_dirs

	def makeAppDirTree(acc, dirs):
		(parent, child) = dirs
		
		children = acc.get(parent, [])
		children.append(child)
		acc[parent] = children

		return acc

	tree = reduce(makeAppDirTree, scanSrcDirs(None, root, None), {})

	app_dirs = []
	parents  = set(tree.keys())
	for app_dir in parents:
		if parents & set(tree[app_dir]) == set():
			app_dirs.append(app_dir)
	return app_dirs

def retrieveCode(target, codebase, skip_update=False):
	(name, url) = codebase
	target_dir  = PyPath.makeRelative(os.path.join(target, name))
	
	if name not in self.updated_repos:
		self.updated_repos[name] = True
		if not os.path.isdir(target_dir):
			PyLog.log("Fetching", name)
			PyRCS.clone(url, target_dir)
		else:
			if not skip_update:
				PyLog.log("Updating", name)
				PyRCS.update(target_dir)
			else:
				PyLog.log("Skipping", name)
	
	return target_dir

def configure(pconfig_lib, config_lib):
	"""
	configure(config_lib{}) -> config_lib{}
	"""
	config   = FishConfig.PriorityConfig(*[config_lib["cli"], config_lib["env"], config_lib[".fishmonger"]])
	app_dirs = getAppDirs()

	include_dirs = set()
	lib_dirs     = set()
	## Get all config files
	app_dirs     = list(set(["."] + app_dirs))
	for app_dir in app_dirs:
		include_dirs |= set(PyFind.findAllByPattern("*include*", root=child, dirs_only=True))
		lib_dirs     |= set(PyFind.findAllByPattern("*lib*",     root=child, dirs_only=True))

		t_cfg_files  = []
		t_tool_files = []
		for ext in ["", "app"] + FishTC.ShortNames.keys():
			cfg_file = os.path.join(app_dir, ".fishmonger" + (ext if ext is "" else "." + ext))
			config_lib[cfg_file] = cfg_file if os.path.isfile(cfg_file) else {}
			if ext in ["", "app"]:
				t_cfg_files.append(cfg_file)
			else:
				t_tool_files.append(cfg_file)

		t_cfg_files.reverse()
		pconfig_lib[app_dir]     = [config_lib[x] for x in t_cfg_files]


		## Find all dependencies
		for cfg in config_lib:


	return (pconfig_lib, config_lib)

def runCommand(command):
	pass
	

def configureStage(config_lib, stage):
	"""
	configureStage(confoglib{}, string()) -> config_lib{}
	"""

	tool_chains = [tc for (x, tc) in FishTC.Tools.iteritems() if :


	return []

def runStage(config_lib, stage):
	"""
	runStage(ConfigLib(), string()) -> config_lib{}
	"""
	PyLog.log(stage.title() + "...")
	PyLog.increaseIndent()
	map(runCommand, configureStage(config_lib, stage))
	PyLog.decreaseIndent()
