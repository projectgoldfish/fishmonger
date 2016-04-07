## Python3.4
import os
import sys
import functools
import multiprocessing

## PIP
import networkx as NX

## Fishmonger modules included
import fishmonger.sh         as FishSH
import fishmonger.rcs        as FishRCS
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
	target_dir  = target.join(name)
	
	if name not in UpdatedRepos:
		UpdatedRepos[name] = True
		if not target_dir.isdir():
			PyLog.log("Fetching", name)
			FishRCS.clone(url, str(target_dir))
		else:
			if not skip_update:
				PyLog.log("Updating", name)
				FishRCS.update(str(target_dir))
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
		src_dir  = root.join("src")
		if src_dir.isdir():
			"""
			If we have a src dir we need to look in that 
			"""
			app_dirs.append((parent, root))
			dirs = [x for x in src_dir.ls() if x.isdir()]
		
			for d in dirs:
				if d.basename()[0] != ".":
					scanSrcDirs(root, d, app_dirs)

		return app_dirs

	def makeAppDirTree(acc, dirs):
		(parent, child) = dirs
		
		children    = acc.get(parent, [])
		children.append(child)
		acc[parent] = children

		return acc

	root = FishPath.Path(root)
	tree = functools.reduce(makeAppDirTree, scanSrcDirs(None, root, None), {})

	x = 0
	app_dirs = []
	src_dirs = [None]
	while x < len(src_dirs):
		src_dir = src_dirs[x]

		if src_dir not in tree:
			app_dirs.append(src_dir)
		else:
			src_dirs += tree[src_dir]
		x += 1
	return app_dirs

def dependencyName(spec):
	(name, url) = spec
	return PyPath.makeRelative(os.path.join(target, name))

def getCFGFiles(pconfig_lib, config_lib, app_dirs):
	x = 0
	config          = pconfig_lib["system"]
	retrieveCodeFun = functools.partial(retrieveCode, config.get("dependency_dir", "deps"), skip_update=config.get("skip_dep_update", False))
	while x < len(app_dirs): 
		app_dir          = app_dirs[x]
		t_dependencies   = set()
		
		config_lib["gen"]["lib_dirs"]     |= set(app_dir.find(pattern="lib",     dirs_only=True))
		config_lib["gen"]["include_dirs"] |= set(app_dir.find(pattern="include", dirs_only=True))
		
		for ext in ["", "app"] + list(FishTC.ShortNames.values()):
			ext      = ext if ext is "" else "." + ext
			cfg_file = app_dir.join(".fishmonger" + ext)
			config_lib[cfg_file] = cfg_file if cfg_file.isfile() else {}

			dependency_specs = config_lib[cfg_file].get("dependencies", [])
			t_dependencies  |= set(dependency_specs)
		
		t_dep_dirs = FishParallel.processObjects(list(t_dependencies), retrieveCodeFun, max_cores=config.get("max_cores", None), acc0=[])
		for t_dep_dir in t_dep_dirs:
			app_dirs += getAppDirs(t_dep_dir)
		x += 1
	return config_lib

def configure(pconfig_lib, config_lib):
	"""
	configure(config_lib{}) -> config_lib{}
	"""
	config          = pconfig_lib["system"]
	app_dirs        = getAppDirs()
	
	"""
	Get all config files and checkout all needed code
	"""
	config_lib["gen"]["app_dirs"]     = app_dirs
	config_lib["gen"]["lib_dirs"]     = set()
	config_lib["gen"]["include_dirs"] = set()
	config_lib                        = getCFGFiles(pconfig_lib, config_lib, [FishPath.Path(".")])
	config_lib                        = getCFGFiles(pconfig_lib, config_lib, app_dirs)
	
	config_lib["gen"]["lib_dirs"]     = list(config_lib["gen"]["lib_dirs"])	
	config_lib["gen"]["include_dirs"] = list(config_lib["gen"]["include_dirs"])
	
	"""
	Generate all PriorityConfig
	"""
	for app_dir in app_dirs:
		for tool in FishTC.Tools.keys():
			pconfig_lib[(tool, app_dir)] = [
				config_lib["cli"],
				config_lib["env"],
				config_lib[app_dir.join(".fishmonger." + FishTC.ShortNames[tool])],
				config_lib[app_dir.join(".fishmonger.app")],
				config_lib[app_dir.join(".fishmonger")],
				config_lib["./.fishmonger"],
				config_lib["defaults"],
				config_lib["gen"]
			]

	return (pconfig_lib, config_lib)

def configureStage(pconfig_lib, config_lib, stage):
	"""
	configureStage(confoglib{}, string()) -> config_lib{}
	"""

	exclusive_tools = {x : FishTC.Tools[x] for x in FishTC.ExclusiveTools if hasattr(FishTC.Tools[x], stage) and hasattr(getattr(FishTC.Tools[x], stage), "__call__")}
	inclusive_tools = {x : FishTC.Tools[x] for x in FishTC.InclusiveTools if hasattr(FishTC.Tools[x], stage) and hasattr(getattr(FishTC.Tools[x], stage), "__call__")}
	tools           = exclusive_tools.keys() + inclusive_tools.keys()

	external_exclusions   = {}
	used_config           = {}
	dependencies          = {}
	for tool in tools:
		t                 = FishTC.Tools[tool]
		used_config[tool] = {}
		for app_dir in config_lib["gen"]["app_dirs"]:
			if app_dir in external_exclusions:
				continue
			
			atc         = pconfig_lib[(tool, app_dir)]
			stage_files = _stageFiles(tool, app_dir, atc, stage)

			if len(stage_files) is not 0:
				if tool in exclusive_tools:
					external_exclusions[app_dir] = tool
				atc["stage_files"]         = stage_files
				used_config[tool][app_dir] = atc

	graph = NX.DiGraph()
	for tool in used_config:
		for app_dir in used_config[tool]:
			atc              = used_config[tool][app_dir]
			to               = (tool, app_dir)
			dependencies[to] = set()

			"""
			Add an edge for every tool we build after
			"""
			for t in atc.get("build_after_tools", []):
				dependencies[to] |= set([(t, a) for a in used_config[tool]])

			t                 = tool
			dependencies[to] |= set([(t, a) for a in atc.get("build_after_apps", [])])

			graph.add_node(to)
			[graph.add_edge(fr, to) for fr in dependencies[to]]

	return [FishParallel.DependentObject(x, list(dependencies[x])) for x in NX.topological_sort(graph)]

def runStage(pconfig_lib, config_lib, stage):
	"""
	runStage(ConfigLib(), string()) -> config_lib{}
	"""
	config = pconfig_lib["system"]
	PyLog.log(stage.title() + "...")
	PyLog.increaseIndent()
	runCommandFun = functools.partial(runCommand, pconfig_lib, stage)
	commands      = configureStage(pconfig_lib, config_lib, stage)

	FishParallel.processObjects(list(commands), runCommandFun, max_cores=config.get("max_cores", None))
	PyLog.decreaseIndent()

def runCommand(pconfig_lib, stage, command):
	error = None

	(tool, app_dir) = command
	PyLog.log(FishTC.ShortNames[tool] + "(" + str(app_dir.basename()) + ")")
	PyLog.increaseIndent()
	
	atc             = pconfig_lib[command]
	cache_files     = FishCache.fetch((stage, command), {})
	stage_files     = atc["stage_files"]
	updated_files   = stage_files["always"]    if isisntance(stage_files, dict) else []
	transient_files = stage_files["as_needed"] if isinstance(stage_files, dict) else stage_files

	for stage_file in transient_files:
		if stage_file in cache_files and stage_file.stat().st_mtime <= cache_files[stage_file]:
			continue
		updated_files.append(stage_file)

	if len(updated_files) == 0:
		PyLog.log("Up to date...")
		PyLog.decreaseIndent()
		return

	commands = getattr(FishTC.Tools[tool], stage)(app_dir, pconfig_lib[command], updated_files)
	try:
		if commands == None:
			pass
		elif isinstance(commands, list):
			for command in commands:
				if hasattr(command, "__call__"):
					command()
				elif isinstance(command, str):
					result = FishSH.cmd(command, stderr=True, stdout=True)
					if result != 0:
						raise FishExc.FishmongerToolchainException("Error executing shell command.", code=result, command=command)
				else:
					raise FishExc.FishmongerToolchainException("Command is not a function or shell command.", command=command)
		else:
			raise FishExc.FishmongerToolchainException("Tool stages must return None or a list of functions and shell comamdns to execute.", toolchain=tool, action=stage)
	except FishExc.FishmongerException as e:
		error = e
	except Exception as e:
		error = FishExc.FishmongerParallelTaskException(str(e), trace=sys.exc_info())

	PyLog.decreaseIndent()
	if error is not None:
		raise error

	## TODO:
	##     Update stage_files in cache
	for updated_file in updated_files:
		cache_files[updated_file] = updated_file.stat().st_mtime

	FishCache.store((stage, command), cache_files)

def _stageFiles(tool, app_dir, config, stage):
	stage_files   = []
	if getattr(FishTC.Tools[tool], stage + "Files") is not FishTC.API.NOT_IMPLEMENTED:
		stage_files = getattr(FishTC.Tools[tool], stage + "Files")(app_dir, config)
	else:
		stage_files = FishTC.Tools[tool].stageFiles(app_dir, config, stage)
	
	return stage_files


