import os
import sys

import copy

import fishmonger

import fishmonger.config   as FC
import fishmonger.dirflags as DF

import pygraph       as PyGraph

import pybase.config as PyConfig
import pybase.find   as PyFind
import pybase.util   as PyUtil
import pybase.set    as PySet

import pybase.log    as PyLog

import pybase.path   as PyPath

import pyrcs         as PyRCS

if sys.version_info < (2, 7):
	raise "Requires python 2.7+"

class FishMongerException(Exception):
	pass

class FishMonger():
	class DirectoryType():
		project, app, src = range(3)

	def __init__(self, config={}):
		self.updated_repos    = {}

		defaults              = {
			"SKIP_UPDATE" : False
		}

		types                 = {
			"SKIP_UPDATE" : bool
		}

		self.command_list     = []

	def retrieveCode(self, target, codebase, skip_update=False):
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

	def findAppDirs(self, parent=None, root=".", app_dirs=[]):
		app_dirs.append((parent, root))
		src_dir = os.path.join(root, "src")
		PyLog.debug("Finding app dirs in ", src_dir, log_level=6)
		
		nparent = root
		dirs    = []
		if os.path.isdir(src_dir):
			dirs = PyFind.getDirDirs(src_dir)
		else:
			nparent = parent
			dirs    = PyFind.getDirDirs(root)

		PyLog.debug("Found app dirs", dirs, log_level=8)
		for d in dirs:
			if os.path.basename(d)[0] != ".":
				self.findAppDirs(nparent, d, app_dirs)

		return app_dirs

	def configure(self, tool_chains):
		## [Module] -> [ToolChain]
		tool_chains    = [t.ToolChain() for t in tool_chains]
		## [ToolChain] -> {String:ToolChain}
		tool_chains    = {t.name() : t  for t in tool_chains}

		## [ToolChain] -> {String:{}}
		allconfig      = {t : {}        for t in tool_chains}

		## Get the app directories
		app_dirs       = self.findAppDirs(None, ".", PySet.Set())

		## parent dir -> [child_dir]
		children       = {}

		## Examine the directories and determine which tools are used
		## At the same time link children to parents
		file_config  = {}
		env_config   = {}
		tool_config  = {t : {} for t in tool_chains}
		app_config   = {}
		include_dirs = PySet.Set()
		lib_dirs     = PySet.Set()
		for (parent, child) in app_dirs:
			include_dirs.append(PyFind.findAllByPattern("*include*", root=child, dirs_only=True))
			lib_dirs.append(    PyFind.findAllByPattern("*lib*",     root=child, dirs_only=True))

			t_env_config  = {}
			t_app_config  = {}
			if child not in children:
				children[child] = []
			if parent in children:
				children[parent].append(child)
				t_app_config = app_config[parent] 
				t_env_config = env_config[parent] 

			for tool in tool_chains:
				nenv_config  = file_config[os.path.join(child, ".fishmonger")]        if os.path.join(child, ".fishmonger")        in file_config else PyConfig.FileConfig(file=os.path.join(child, ".fishmonger"),         config=env_config[parent].config        if parent in env_config        else {})
				ntool_config = file_config[os.path.join(child, ".fishmonger" + tool)] if os.path.join(child, ".fishmonger" + tool) in file_config else PyConfig.FileConfig(file=os.path.join(child, ".fishmonger." + tool), config=tool_config[tool][parent].config if parent in tool_config[tool] else tool_chains[tool].defaults)
				napp_config  = file_config[os.path.join(child, ".fishmonger.app")]    if os.path.join(child, ".fishmonger.app")    in file_config else PyConfig.FileConfig(file=os.path.join(child, ".fishmonger.app"),     config=app_config[parent].config        if parent in app_config        else {})

				env_config[child]        = nenv_config
				tool_config[tool][child] = ntool_config
				app_config[child]        = napp_config

				app_tool_config          = FC.AppToolConfig(
					child,
					nenv_config,
					ntool_config,
					napp_config
				)
				if parent in allconfig[tool]:
					app_tool_config.parent   = allconfig[tool][parent]
					app_tool_config.src_root = allconfig[tool][parent]._dir
					allconfig[tool][parent].children.append(app_tool_config)

				allconfig[tool][child]   = app_tool_config

				dep_dirs = [(".", self.retrieveCode(app_tool_config["DEP_DIR"], x, skip_update=app_tool_config["SKIP_UPDATE"])) for x in app_tool_config["DEPENDENCIES"]]
				for (ignore, dep_dir) in dep_dirs:
					app_dirs.append(self.findAppDirs(".", dep_dir, PySet.Set()))

		for tool in allconfig:
			for child in allconfig[tool]:
				allconfig[tool][child]["INCLUDE_DIRS"] = include_dirs
				allconfig[tool][child]["LIB_DIRS"]     = lib_dirs

			## Update types
			for child in children:
				apptool = allconfig[tool][child]
				## If we have no children and no src dir we are a subdir
				if len(apptool.children) == 0 and not os.path.isdir(os.path.join(child, "src")):
					apptool.type = FC.AppToolConfig.Types.subdir
				## If we have no children but have a subdir we're a shallow app
				elif len(apptool.children) == 0 and os.path.isdir(os.path.join(child, "src")):
					apptool.type = FC.AppToolConfig.Types.app
				else:
					count = len(apptool.children)
					for c in children[child]:
					#	print "\t", os.path.join(c, "src")
						if os.path.isdir(os.path.join(c, "src")):
							count -= 1

					#print "TYPE REDUX", len(apptool.children), count, apptool.name()

					## We have children and all have a src dir; We're a project
					if count == 0:
						apptool.type = FC.AppToolConfig.Types.project
					## If we're not a project and not a subdir we're an app
					else:
						apptool.type = FC.AppToolConfig.Types.app

		self.allconfig = allconfig
		self.children  = children
		PyLog.debug("Child map", children, log_level=1)
		PyLog.debug("Generated Config", allconfig, log_level=9)

	## We have to detect the applicaiton folders and generate base app
	## configurations here. Caling doConfigure will fill in the blanks.
	## Once we do that we can setup the tool chains
	def configureAction(self, tool_chains, action):
		(external_tools, internal_tools) = tool_chains
		tool_chains                      = external_tools + internal_tools
		## [Module] -> [ToolChain]
		tool_chains    = [t.ToolChain() for t in tool_chains]
		## [ToolChain] -> {String:ToolChain}
		tool_chains    = {t.name() : t  for t in tool_chains}

		external_tools = [t.ToolChain().name() for t in external_tools]

		allconfig      = self.allconfig
		children       = copy.copy(self.children)

		usedconfig     = {}

		external_exclusions = {}
		## Figure out which nodes are used
		for tool in tool_chains:
			for child in children:
				apptool = allconfig[tool][child]

				if apptool.type == FC.AppToolConfig.Types.subdir:
					PyLog.debug("Child is just a subdir. Let parent build it", child, log_level=5)
					continue

				if apptool.type == FC.AppToolConfig.Types.project:
					PyLog.debug("Child is just a project. Just build it's kids", child, log_level=5)
					continue

				if child in external_exclusions:
					PyLog.debug("Child used by previous external tool. Cannot be used again", child, external_exclusions[child], log_level=5)
					external_exclusions[child] = tool
					continue			

				if tool_chains[tool].uses(apptool):
					## Since we're used update our children so we only use the relevant ones
					apptool = apptool.clone(apptool._dir)
					apptool.children = [c for c in apptool.children if tool_chains[tool].uses(c)]
					
					if tool in external_tools:
						external_exclusions[child] = tool
					PyLog.debug("Users of Tool", tool, child, log_level=8)
					if tool not in usedconfig:
						usedconfig[tool]    = {}
					usedconfig[tool][child] = apptool

		allconfig = usedconfig
		PyLog.debug("Updated Config", allconfig, log_level=9)
		
		vertexes   = PySet.Set()
		for tool in allconfig:
			for child in allconfig[tool]:
				apptool = allconfig[tool][child]
				name    = apptool.name()

				## Build graph of dependencies
				edges = PySet.Set()
				root  = apptool.path(DF.source|DF.root)

				## If we build after a tool we build after all nodes of that tool
				after_tools = PySet.Set()
				for t in apptool["BUILD_AFTER_TOOLS"]:
					## Add an edge for each app that uses this tool
					after_tools.append([(t, allconfig[t][a].name()) for a in allconfig[t]])
					edges.append(after_tools)
				PyLog.debug("After tools", after_tools, log_level=8)
				edges.append(after_tools)

				## If we build after apps we build after them for each tool
				## Since we're iterating for each tool we'll get to adding those nodes eventually
				after_apps = PySet.Set()
				for after in apptool["BUILD_AFTER_APPS"]:
					## We may be told to build after ourself...
					## Don't do that
					if after == name:
						PyLog.warning("Attemping to build ourself after ourself... This seems silly please fix that")
						continue
					if after in allconfig[tool]:
						after_apps.append((tool, after))

				PyLog.debug("App and Afters", (tool, name), after_apps, log_level=8)
				edges.append(after_apps)

				## Add specific requirements
				edges.append(apptool["BUILD_AFTER"])

				PyLog.debug("Edges", edges, log_level=8)
				vertexes.append(PyGraph.Vertex((tool, name), edges, data={"tool":tool, "root":root}))

		sorted_vertexes = [v.name for v in vertexes]
		sorted_vertexes.sort()
		PyLog.debug("Vertexes", sorted_vertexes, log_level=6)

		## Graph the vertexes
		digraph    = PyGraph.DiGraph(vertexes)
		
		## Get order and strip out values we want
		taskorders = digraph.topologicalOrder()
		## Correct order
		taskorders.reverse()

		PyLog.debug("Build order", taskorders, log_level=7)

		self.command_list = [(getattr(tool_chains[digraph[order]["tool"]], action), allconfig[digraph[order]["tool"]][digraph[order]["root"]]) for order in taskorders]

	## We have to detect the applicaiton folders and generate base app
	## configurations here. Caling doConfigure will fill in the blanks.
	## Once we do that we can setup the tool chains
	def packageConfigure(self, tool_chains, action):
		(external_tools, internal_tools) = tool_chains
		tool_chains                      = external_tools + internal_tools

		self.command_list = []
		if tool_chains == []:
			return

		## [Module] -> [ToolChain]
		tool_chains    = [t.ToolChain() for t in tool_chains]
		## [ToolChain] -> {String:ToolChain}
		tool_chains    = {t.name() : t for t in tool_chains}

		external_tools = [t.ToolChain() for t in external_tools]
		external_tools = {t.name() : t for t in external_tools}

		## We just need the SRC_DIR from the root config to get started
		base_config  = PyConfig.FileConfig(file=".fishmonger", defaults={})
		
		allconfig    = {}
		dependencies = PySet.Set("src")
		
		PyLog.debug("Fetching dependencies")
		PyLog.increaseIndent()

		## We only want to search these out once
		t_env_config  = PyConfig.FileConfig(file=".fishmonger")
		t_app_config  = PyConfig.FileConfig(file=".fishmonger.app")
		
		tool_config = {}
		for tool_chain in tool_chains:
			tool_config[tool_chain] = PyConfig.FileConfig(file=".fishmonger." + tool_chain, config=tool_chains[tool_chain].defaults)
						
		for tool_chain in tool_chains:
			## For every directory merge the configs

			app_config = FC.AppToolConfig(
				".",
				t_env_config,
				None,
				None
			)

			app_config.children = [1]

			src_configs = tool_chains[tool_chain].uses(app_config)
			app_config.src_configs = src_configs
			if len(app_config.src_configs) != 0:
				allconfig[tool_chain] = app_config
			
		PyLog.decreaseIndent()		

		## build command list
		self.command_list = [(getattr(tool_chains[tool_chain], action), allconfig[tool_chain]) for tool_chain in allconfig]

	def runAction(self):
		for (action, app) in self.command_list:
			res = action(app)
			if res == False:
				PyLog.error("Action returned failure", action, app)
				sys.exit(1)

	def build(self, tools):
		PyLog.log("Building")
		PyLog.increaseIndent()
		self.configureAction(tools, "build")
		self.runAction()
		PyLog.decreaseIndent()

	def install(self, tools):
		PyLog.log("Installing")
		PyLog.increaseIndent()
		self.configureAction(tools, "install")
		self.runAction()
		PyLog.decreaseIndent()

	def document(self, tools):
		PyLog.log("Documenting")
		PyLog.increaseIndent()
		self.configureAction(tools, "document")
		self.runAction()
		PyLog.decreaseIndent()

	def clean(self, tools):
		PyLog.log("Cleaning")
		PyLog.increaseIndent()
		self.configureAction(tools, "clean")
		self.runAction()
		PyLog.decreaseIndent()

	def generate(self, tools):
		PyLog.log("Generating")
		PyLog.increaseIndent()
		self.configureAction(tools, "generate")
		self.runAction()
		PyLog.decreaseIndent()

	def link(self, tools):
		PyLog.log("Linking")
		PyLog.increaseIndent()
		self.configureAction(tools, "link")
		self.runAction()
		PyLog.decreaseIndent()

	def package(self, tools):
		PyLog.log("Packaging")
		PyLog.increaseIndent()
		self.packageConfigure(tools, "package")
		self.runAction()
		PyLog.decreaseIndent()

def main():
	cli = PyConfig.CLIConfig()

	PyLog.setLogLevel(0 if "LOG_LEVEL" not in cli else int(cli["LOG_LEVEL"]))
	
	fishmonger.addInternalToolChains(cli.get("INTERNAL_TOOL", []))
	fishmonger.addExternalToolChains(cli.get("EXTERNAL_TOOL", []))
	fishmonger.addGenerateToolChains(cli.get("GENERATE_TOOL", []))
	fishmonger.addBuildToolChains(   cli.get("BUILD_TOOL",    []))
	fishmonger.addLinkToolChains(    cli.get("LINK_TOOL",     []))
	fishmonger.addInstallToolChains( cli.get("INSTALL_TOOL",  []))
	fishmonger.addDocumentToolChains(cli.get("DOC_TOOL",      []))
	fishmonger.addPackageToolChains( cli.get("PACKAGE_TOOL",  []))

	fish                = FishMonger()

	tools_for_all       = fishmonger.InternalToolChains
	
	actions = {}
	actions["clean"]    = [(fish.clean, tools_for_all)]

	actions["build"]    = [
		(fish.generate, tools_for_all + fishmonger.GenerateToolChains),
		(fish.build,    tools_for_all + fishmonger.BuildToolChains),
		(fish.link,     tools_for_all + fishmonger.LinkToolChains)
	]
	actions["compile"]  = actions["build"]

	actions["install"]  = [(fish.install,  tools_for_all + fishmonger.InstallToolChains)]
	actions["doc"]      = [(fish.document, tools_for_all + fishmonger.DocumentToolChains)]
	actions["document"] = actions["doc"]
	
	actions["package"]  = [(fish.package,  fishmonger.PackageToolChains)]

	actions["test"]     = [(None, [])]

	x = 0;
	if x not in cli:
		PyLog.error("Usage: fishmonger <clean|build|compile|install|doc|document>")
		return 1

	PyLog.log("Configuring")
	PyLog.increaseIndent()
	fish.configure(fishmonger.AllToolChains.values())
	PyLog.decreaseIndent()

	while cli[x] in actions:
		tasks = actions[cli[x]]
		for (task, tools) in tasks:
			task((fishmonger.ExternalToolChains, tools))
		x += 1

main()