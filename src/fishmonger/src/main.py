#! /usr/bin/python
import os
import sys

import fishmonger

import fishmonger.config

import pygraph       as PyGraph

import pybase.config as PyConfig
import pybase.find   as PyFind
import pybase.util   as PyUtil
import pybase.set    as PySet

import pybase.log    as PyLog

import pybase.path   as PyPath

import pyrcs         as PyRCS

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

		self.root_config      = PyConfig.Config(defaults=defaults, types=types)
		self.root_config.merge(PyConfig.SysConfig())
		self.root_config.merge(PyConfig.CLIConfig())


	def retrieveCode(self, target, codebase, skip_update=False):
		(name, url) = codebase
		target_dir  = os.path.join(target, name)
		
		if name not in self.updated_repos:
			self.updated_repos[name] = True
			if not os.path.isdir(target_dir):
				PyLog.output("Fetching", name)
				PyRCS.clone(url, target_dir)
			else:
				if not skip_update:
					PyLog.output("Updating", name)
					PyRCS.update(target_dir)
				else:
					PyLog.output("Skipping", name)
		
		return target_dir

	## Updates the config map so apps point to eaach other
	## and know of thier source directories
	def determineDirTypes(self, root, config_map):

		config     = config_map[root]

		dirs       = []
		src_dir    = os.path.join(root, config["SRC_DIR"])
		if os.path.isdir(src_dir):
			dirs   = PyFind.getDirDirs(src_dir)
			if dirs == []:
				dirs = [src_dir]
		else:
			dirs   = PyFind.getDirDirs(root)
		
		f_all      = PySet.Set()
		f_apps     = PySet.Set()
		f_sources  = PySet.Set()

		for dir in dirs:
			(all_apps, apps, sources) = self.determineDirTypes(dir, config_map)

			f_all      += all_apps
			f_apps     += apps
			f_sources  += sources

		if f_apps != []:
			## We are parent to apps.
			for f_app in f_apps:
				config_map[f_app].parent = config
			config_map[root].children    = [config_map[t] for t in f_sources]
			config_map[root].src_dirs    = list(f_sources)
			return (f_all + [root] + f_apps, [root], PySet.Set())
		elif f_sources != []:
			if os.path.isdir(src_dir):
				## We have a SRC_DIR! We are definitely an app
				config_map[root].children =  [config_map[t] for t in f_sources + [src_dir]]
				config_map[root].src_dirs = list(f_sources)

				## Tag the src_roots
				for child in config_map[root].children:
					child.app_root = os.path.dirname(src_dir)
					child.src_root = src_dir

				return (f_all + [root], [root], PySet.Set())
			else:
				## No SRC_DIR we're another source dir
				return (f_all, f_apps,  f_sources + [root])
		elif f_apps == [] and f_sources == []:
			## We're just a lowly SRC_DIR
			return (PySet.Set(), PySet.Set(), [root])
		else:
			raise FishMongerException("Problem parsing directory types: " + root)

	## We have to detect the applicaiton folders and generate base app
	## configurations here. Caling doConfigure will fill in the blanks.
	## Once we do that we can setup the tool chains
	def configure(self, tool_chains, action):
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
		base_config  = PyConfig.FileConfig(file=".fishmonger", defaults={"SRC_DIR":"src"})
		
		allconfig    = {t : {} for t in tool_chains}
		dependencies = PySet.Set(base_config["SRC_DIR"])
		
		PyLog.output("Fetching dependencies")
		PyLog.increaseIndent()

		## We only want to search these out once
		t_env_config  = PyConfig.FileConfig(file=".fishmonger")
		t_app_config  = PyConfig.FileConfig(file=".fishmonger.app")
		
		t_tool_config = {}
		for tool_chain in tool_chains:
			t_tool_config[tool_chain] = PyConfig.FileConfig(file=".fishmonger." + tool_chain, config=tool_chains[tool_chain].defaults)
			
		for dependency in dependencies:
			dependency   = PyPath.makeRelative(dependency)

			## We only want to search these out once
			env_config   = fishmonger.config.ConfigTree(dir=dependency, file=".fishmonger",     config=t_env_config.config)
			app_config   = fishmonger.config.ConfigTree(dir=dependency, file=".fishmonger.app", config=t_app_config.config)
		
			## Generate FULL config for each Tool/Directory
			## config will be a mapping[tool_name][app_dir]
			
			for tool_chain in tool_chains:
				## get this toolchains ConfigTree
				tool_config = fishmonger.config.ConfigTree(dir=dependency, file=".fishmonger." + tool_chain, config=t_tool_config[tool_chain].config)

				## For every directory merge the configs
				for dir in app_config.getNodes():
					allconfig[tool_chain][dir] = fishmonger.config.AppToolConfig(
						dir,
						env_config[dir],
						tool_config[dir],
						app_config[dir]
					)

			## We pick first as we do not allow DEPENDENCIES on a tool chain
			## so it doesnt matter which we use
			tool = tool_chains.keys()[0]
			for dir in allconfig[tool]:
				dep_dirs   = [self.retrieveCode(allconfig[tool][dir]["DEP_DIR"], x, skip_update=allconfig[tool][dir]["SKIP_UPDATE"]) for x in allconfig[tool][dir]["DEPENDENCIES"]]
				after_apps = [x for (x, y) in allconfig[tool][dir]["DEPENDENCIES"]]

				## Update all instances of the app with the build_after app tokens for the dependencies
				##
				## THIS IS BROKEN: Leave commented out until it can be properly reworked.
				## Have apps declare their own BUILD_AFTER_APPS for now
				##for ttool in allconfig:
				##	allconfig[ttool][dir]["BUILD_AFTER_APPS"].append(after_apps)
					
				dependencies.append(dep_dirs)
		PyLog.decreaseIndent()

		## Find INCLUDE_DIRS
		include_dirs = PySet.Set()
		lib_dirs     = PySet.Set()
		for dependency in dependencies:
			include_dirs.append(PyFind.findAllByPattern("*include*", root=dependency, dirs_only=True))
			lib_dirs.append(    PyFind.findAllByPattern("*lib*",     root=dependency, dirs_only=True))

		## Update config with found INCLUDE_DIRS
		for t in allconfig:
			for a in allconfig[t]:
				allconfig[t][a]["INCLUDE_DIRS"] = include_dirs
				allconfig[t][a]["LIB_DIRS"]     = lib_dirs

		## Get the apps that we need to build
		apps = PySet.Set()
		for tool in tool_chains:		
			[apps.append(self.determineDirTypes(PyPath.makeRelative(d), allconfig[tool])[0]) for d in dependencies]
	
		## Determine who uses what
		to_del = PySet.Set()
		for t_key in allconfig:
			for a_key in allconfig[t_key]:
				app   = allconfig[t_key][a_key]

				## If the app has no src_dirs it has nothing to build
				if app.src_dirs == []:
					to_del.append((t_key, a_key))
					continue

				## Update src_dirs to just those this tool will use
				uses = tool_chains[t_key].uses(app)

				if not uses:
					## If there are no src_dirs found this app doesnt use this tool.
					to_del.append((t_key, a_key))
					continue

				if t_key in external_tools:
					## If it's an external tool we only allow it to process this app
					for tt_key in allconfig:
						if tt_key == t_key:
							continue
						to_del.append((tt_key, a_key))


		for (t_key, a_key) in to_del:
			del allconfig[t_key][a_key]

		for t_tool in allconfig:
			tool_chains[t_tool].apps = allconfig[t_tool].values()

		## Determine Vertexes
		vertexes   = PySet.Set()
		for t_key in allconfig:
			tool      = t_key
			for a_key in allconfig[t_key]:
				app   = allconfig[t_key][a_key]
				name  = app.name()

				## Build graph of dependencies
				edges = PySet.Set()
				root  = app.root()

				## If we build after a tool we build after all nodes of that tool
				after_tools = PySet.Set()

				#print "\nNODES", t_key, a_key
				for t in app["BUILD_AFTER_TOOLS"]:
					after_tools.append([(t, allconfig[t][a].name()) for a in allconfig[t]])
					edges.append(after_tools)
				#print "TOOLS:", after_tools
				edges.append(after_tools)

				## If we build after apps we build after them for each tool
				## Since we're iterating for each tool we'll get to adding those nodes eventually
				after_apps = PySet.Set()
				for a in app["BUILD_AFTER_APPS"]:
					## We may be told to build after ourself...
					## Don't do that
					if a == name:
						continue
					for aa_key in allconfig[t_key]:
						if allconfig[t_key][aa_key].name() == a:
							after_apps.append((t_key, allconfig[t_key][aa_key].name()))
				#print "APPS:", after_apps, app["BUILD_AFTER_APPS"]
				edges.append(after_apps)

				## Add specific requirements
				edges.append(app["BUILD_AFTER"])

				#print "EDGES", edges

				vertexes.append(PyGraph.Vertex((tool, name), edges, data={"tool":tool, "root":root}))
		
		## Graph the vertexes
		digraph    = PyGraph.DiGraph(vertexes)
		
		## Get order and strip out values we want
		taskorders = digraph.topologicalOrder()
		## Correct order
		taskorders.reverse()
	
		## build command list
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
		base_config  = PyConfig.FileConfig(file=".fishmonger", defaults={"SRC_DIR":"src"})
		
		allconfig    = {}
		dependencies = PySet.Set(base_config["SRC_DIR"])
		
		PyLog.output("Fetching dependencies")
		PyLog.increaseIndent()

		## We only want to search these out once
		t_env_config  = PyConfig.FileConfig(file=".fishmonger")
		t_app_config  = PyConfig.FileConfig(file=".fishmonger.app")
		
		tool_config = {}
		for tool_chain in tool_chains:
			tool_config[tool_chain] = PyConfig.FileConfig(file=".fishmonger." + tool_chain, config=tool_chains[tool_chain].defaults)
						
		for tool_chain in tool_chains:
			## For every directory merge the configs

			app_config = fishmonger.config.AppToolConfig(
				".",
				t_env_config,
				None,
				None
			)

			app_config.children = [1]

			if tool_chains[tool_chain].uses(app_config):
				allconfig[tool_chain] = app_config
			
		PyLog.decreaseIndent()		

		## build command list
		self.command_list = [(getattr(tool_chains[tool_chain], action), allconfig[tool_chain]) for tool_chain in allconfig]


	def runAction(self):
		for (action, app) in self.command_list:
			action(app)

	def build(self, tools):
		PyLog.output("Building")
		PyLog.increaseIndent()
		self.configure(tools, "build")
		self.runAction()
		PyLog.decreaseIndent()

	def install(self, tools):
		PyLog.output("Installing")
		PyLog.increaseIndent()
		self.configure(tools, "install")
		self.runAction()
		PyLog.decreaseIndent()

	def document(self, tools):
		PyLog.output("Documenting")
		PyLog.increaseIndent()
		self.configure(tools, "document")
		self.runAction()
		PyLog.decreaseIndent()

	def clean(self, tools):
		PyLog.output("Cleaning")
		PyLog.increaseIndent()
		self.configure(tools, "clean")
		self.runAction()
		PyLog.decreaseIndent()

	def generate(self, tools):
		PyLog.output("Generating")
		PyLog.increaseIndent()
		self.configure(tools, "generate")
		self.runAction()
		PyLog.decreaseIndent()

	def link(self, tools):
		PyLog.output("Linking")
		PyLog.increaseIndent()
		self.configure(tools, "link")
		self.runAction()
		PyLog.decreaseIndent()

	def package(self, tools):
		PyLog.output("Packaging")
		PyLog.increaseIndent()
		self.packageConfigure(tools, "package")
		self.runAction()
		PyLog.decreaseIndent()

def main():
	cli = PyConfig.CLIConfig()

	x = 1;
	extraToolChains = []
	while x in cli:
		extraToolChains.append(cli[x])
		x += 1

	fishmonger.addInternalToolChains(extraToolChains)
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

	
	if cli[0] in actions:
		tasks = actions[cli[0]]
		for (task, tools) in tasks:
			task((fishmonger.ExternalToolChains, tools))
	else:
		PyLog.output("Usage: fishmonger <clean|build|compile|install|doc|document> [ToolChain[s]]")
		return 0
		
main()