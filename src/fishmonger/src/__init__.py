## Python modules included
import os
import sys

import functools

import multiprocessing

## Dependency imports
import networkx as NX

## RlesZilm imports
import pyrcs                 as PyRCS
import pybase.log            as PyLog

## Fishmonger modules included
import fishmonger.path       as FishPath
import fishmonger.cache      as FishCache
import fishmonger.config     as FishConfig
import fishmonger.exceptions as FishExc
import fishmonger.toolchains as FishTC
import fishmonger.parallel   as FishParallel

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

Manager       = multiprocessing.Manager()
UpdatedRepos  = Manager.dict()

def retrieveCode(target, spec, skip_update=False):
	target      = target if isinstance(target, FishPath.Path) else FishPath.Path(target)
	(name, url) = spec
	target_dir  = target.join(name).relative()
	
	if name not in UpdatedRepos:
		UpdatedRepos[name] = True
		if not target_dir.isdir():
			PyLog.log("Fetching", name)
			PyRCS.clone(url, str(target_dir))
		else:
			if not skip_update:
				PyLog.log("Updating", name)
				PyRCS.update(str(target_dir))
			else:
				PyLog.log("Skipping", name)
	
	return target_dir


def getAppDirs(root = "."):
	"""
	getAppDirs(string()|path()::Root) -> [path()]::Return

	Scans the directory structure to determine the application directories.

	Root   - The Directory to start scanning from.

	Return - A list of directories that are root directories for applications
	"""

	def scanSrcDirs(parent=None, root=".", app_dirs=None):
		"""
		scanSrcDirs(string()::Parent, string()::Root, [()]|None::AppDirs) ->

		Scans the directory structure for src directories and thier parents.
		"""
		
		root     = root if isinstance(root, FishPath.Path) else FishPath.Path(root)
		app_dirs = app_dirs if app_dirs is not None else []
		
		app_dirs.append((parent, root))
		src_dir  = root.join("src")
		
		nparent  = root
		dirs     = []
		if src_dir.isdir():
			dirs = src_dir.find(dirs_only=True)
		else:
			nparent = parent
			dirs    = root.find(dirs_only=True)

		for d in dirs:
			if d.basename()[0] != ".":
				scanSrcDirs(nparent, d, app_dirs)

		return app_dirs

	def makeAppDirTree(acc, dirs):
		(parent, child) = dirs
		
		children    = acc.get(parent, [])
		children.append(child)
		acc[parent] = children

		return acc

	root = FishPath.Path(root)
	tree = reduce(makeAppDirTree, scanSrcDirs(None, root, None), {})

	app_dirs = []
	parents  = set(tree.keys())
	for app_dir in parents:
		if parents & set(tree[app_dir]) == set():
			app_dirs.append(app_dir)
	return app_dirs

def dependencyName(spec):
	(name, url) = spec
	return PyPath.makeRelative(os.path.join(target, name))

def configure(pconfig_lib, config_lib):
	"""
	configure(config_lib{}) -> config_lib{}
	"""
	
	configured      = False
	config          = FishConfig.PriorityConfig(*[config_lib["cli"], config_lib["env"], config_lib["./.fishmonger"]])
	
	app_dirs        = getAppDirs()
	
	include_dirs    = set()
	lib_dirs        = set()

	## Get all config files
	app_dirs        = list(set([FishPath.Path("./")] + app_dirs))
	retrieveCodeFun = functools.partial(retrieveCode, config.get("dependency_dir", "deps"), skip_update=config.get("skip_dep_update", False))
	
	"""
	Get all config files and checkout all needed code
	"""
	x = 0
	while x < len(app_dirs): 
		app_dir          = app_dirs[x]
		t_dependencies   = set()
		
		include_dirs    |= set(app_dir.find(pattern="include", dirs_only=True))
		lib_dirs        |= set(app_dir.find(pattern="lib",     dirs_only=True))
		for ext in ["", "app"] + FishTC.ShortNames.values():
			ext      = ext if ext is "" else "." + ext
			cfg_file = app_dir.join(".fishmonger" + ext)
			config_lib[cfg_file] = cfg_file if cfg_file.isfile() else {}

			dependency_specs = config_lib[cfg_file].get("dependencies", [])
			t_dependencies  |= set(dependency_specs)
		
		[app_dirs.append(dep_dir) for dep_dir in FishParallel.processObjects(list(t_dependencies), retrieveCodeFun, max_cores=config.get("max_cores", None), acc0=[])]
		x += 1	
		
	config_lib["gen"]["include_dirs"] = list(include_dirs)
	config_lib["gen"]["lib_dirs"]     = list(lib_dirs)
	config_lib["gen"]["app_dirs"]     = app_dirs

	"""
	Generate all PriorityConfig
	"""
	print "++++++++"
	for app_dir in app_dirs:
		for tool in FishTC.Tools.keys():
			print (tool, app_dir)
			pconfig_lib[(tool, app_dir)] = [
				config_lib["cli"],
				config_lib["env"],
				config_lib[app_dir.join(".fishmonger." + FishTC.ShortNames[tool])],
				config_lib[app_dir.join(".fishmonger.app")],
				config_lib[app_dir.join(".fishmonger")],
				config_lib["./.fishmonger"],
				config_lib["gen"]
			]
	print "++++++++"

	return (pconfig_lib, config_lib)

def configureStage(pconfig_lib, config_lib, stage):
	"""
	configureStage(confoglib{}, string()) -> config_lib{}
	"""

	exclusive_tools = {x : FishTC.Tools[x] for x in FishTC.ExclusiveTools if hasattr(FishTC.Tools[x], stage) and hasattr(getattr(FishTC.Tools[x], stage), "__call__")}
	inclusive_tools = {x : FishTC.Tools[x] for x in FishTC.InclusiveTools if hasattr(FishTC.Tools[x], stage) and hasattr(getattr(FishTC.Tools[x], stage), "__call__")}

	print "--------"
	for k in pconfig_lib.keys():
		print k
	print "--------"

	tools = exclusive_tools.keys() + inclusive_tools.keys()

	print tools

	external_exclusions   = {}
	used_config           = {}
	for tool in tools:
		t                 = FishTC.Tools[tool]
		used_config[tool] = {}
		print t
		for app_dir in config_lib["gen"]["app_dirs"]:
			print "Check", t, app_dir
			if app_dir in external_exclusions:
				continue
			atc = pconfig_lib[(tool, app_dir)]

			print "Tool", t

			if t.uses(app_dir, atc):
				if tool in exclusive_tools:
					external_exclusions[app_dir] = tool
				used_config[tool][app_dir] = atc

	print used_config
	graph = NX.DiGraph()

	for tool in used_config:
		for app_dir in used_config[tool]:
			atc = used_config[tool][app_dir]

			to  = (tool, app_dir)

			"""
			Add an edge for every tool we build after
			"""
			for t in atc.get("build_after_tools", []):
				[graph.add_edge((t, a), to) for a in used_config[tool]]

			t = tool
			[graph.add_edge(t, a) for a in atc.get("build_after_apps", []) if a is not app_dir]

	print "Order",  NX.topological_sort(graph)
	return NX.topological_sort(graph)

def runStage(pconfig_lib, config_lib, stage):
	"""
	runStage(ConfigLib(), string()) -> config_lib{}
	"""
	PyLog.log(stage.title() + "...")
	PyLog.increaseIndent()
	map(runCommand, configureStage(pconfig_lib, config_lib, stage))
	PyLog.decreaseIndent()

def runCommand(command):
	pass
	