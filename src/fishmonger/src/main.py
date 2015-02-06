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

import pybase.path   as PyPath

import pyrcs         as PyRCS

class FishMongerException(Exception):
	pass

class FishMonger():
	class DirectoryType():
		project, app, src = range(3)

	def __init__(self, config={}):
		self.updated_repos    = {}

	def retrieveCode(self, target, codebase):
		(name, url) = codebase
		target_dir  = os.path.join(target, name)
		
		if name not in self.updated_repos:
			self.updated_repos[name] = True
			if not os.path.isdir(target_dir):
				print "====> Fetching:", name
				PyRCS.clone(url, target_dir)
			else:
				if self.env_config["SKIP_UPDATE"].upper() != "TRUE":
					print "====> Updating:", name
					PyRCS.update(target_dir)
				else:
					print "====> Skipping:", name
		else:
			print "====> Skipping:", name
		return target_dir

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
		
		print root, dirs

		f_all      = []
		f_apps     = []
		f_sources  = []

		for dir in dirs:
			(all_apps, apps, sources) = self.determineDirTypes(dir, config_map)

			f_all      += all_apps
			f_apps     += apps
			f_sources  += sources

		if f_apps != []:
			## We are parent to apps.
			for f_app in f_apps:
				config_map[f_app].parent = config
			config_map[root].src_dirs    = f_sources
			return (f_all + [root] + f_apps, [root], [])
		elif f_sources != []:
			if os.path.isdir(src_dir):
				## We have a SRC_DIR! We are definitely an app
				config_map[root].src_dirs = f_sources + [src_dir]
				return (f_all + [root], [root], [])
			else:
				## No SRC_DIR we're another source dir
				return (f_all, [],  [root] + f_sources)
		elif f_apps == [] and f_sources == []:
			## We're just a lowly SRC_DIR
			return (f_all, [], [root])
		else:
			raise FishMongerException("Problem parsing directory types: " + root)


	## We have to detect the applicaiton folders and generate base app
	## configurations here. Caling doConfigure will fill in the blanks.
	## Once we do that we can setup the tool chains
	def configure(self, tool_chains, action):
		print tool_chains
		## [Module] -> [ToolChain]
		tool_chains = [t.ToolChain() for t in tool_chains]
		## [ToolChain] -> {String:ToolChain}
		tool_chains = {t.getName() : t for t in tool_chains}

		print "\n",tool_chains

		## Go through our directories and build out configuration for each type
		## env_config/app_config are app_dir -> FileConfig
		env_config  = fishmonger.config.ConfigTree(file=".fishmonger")
		app_config  = fishmonger.config.ConfigTree(file=".fishmonger.app")
		## tool_config is tool name -> app_dir -> FileConfig
		tool_config = {t : fishmonger.config.ConfigTree(file=".fishmonger." + t) for t in tool_chains.keys()}

		#print app_config["./src/fishmonger/src/toolchains"]
		print tool_config
		print "\t\t\t"
		print app_config.getNodes()
		exit(0)
		## Generate FULL config for each Tool/Directory
		config      = {}
		for tool in tool_config:
			t_config = {}
			
			for dir in env_config.getNodes():
				##print "Tree", env_config[dir]

				##print "Building config for", dir
				##print "\tEnv", env_config[dir].config.config
				##print "\tToo", tool_config[tool][dir].config.config
				#print "\tApp", app_config[dir].config.config

				t_config[dir] = fishmonger.config.AppConfig(
					dir,
					env_config[dir].config,
					tool_config[tool][dir].config,
					app_config[dir].config
				)

				print "\nAPP", t_config[dir].config

			

			t_apps     = PySet.Set()
			t_src_dirs = PySet.Set([PyPath.makeRelative(t_config["."]["SRC_DIR"])])
			
			for t_src_dir in t_src_dirs:
				print ":::", t_src_dir
				(tt_apps, x, y) = self.determineDirTypes(t_src_dir, t_config)
				
				for ttt_app in PySet.Set(tt_apps):
					print "===", ttt_app, t_config[ttt_app]["DEPENDENCIES"]
					tt_config = t_config[ttt_app]
					for d in tt_config["DEPENDENCIES"]:
						print "---", d
						t_src_dirs.append(PyPath.makeRelative(self.retrieveCode(tt_config["DEP_DIR"], d)))
						
				t_apps += tt_apps
				print t_apps

			config[tool] = {t : t_config[t] for t in t_apps}
			

		## Filter tool_chains to those usable
		used_tool_chains = []
		for tool in tool_chains:
			if tool_chains[tool].uses(config[tool].values()) != []:
				used_tool_chains.append(tool)
		self.tool_chains = {t : tool_chains[t] for t in used_tool_chains}

		## Determine Vertexes
		vertexes  = PySet.Set()
		for tool in used_tool_chains:
			for app in config[tool]:
				edges = PySet.Set()

				app = config[tool][app]
				
				t_app_name = app.getName()

				if app.parent:
					edges.append((tool,app.parent.getName()))

				## If we build after a tool we build after all nodes of that tool
				for t in app["BUILD_AFTER_TOOLS"]:
					edges.append([(t, t_a) for t_a in tool_chains[t]])

				## If we build after apps just add them for this tool.
				## these will be taken care of on each tool level
				edges.append([(tool, a) for a in app["BUILD_AFTER_APPS"]])

				## Add specific requirements
				edges.append(app["BUILD_AFTER"])

				vertexes.append(((tool, t_app_name), edges))

		## Graph the vertexes
		digraph = PyGraph.DiGraph([PyGraph.Vertex(v) for v in vertexes])
		
		## Get order and strip out values we want
		order   = [x for (x, y) in digraph.topologicalOrder()]
		## Correct order
		order.reverse()
		
		## build command list
		self.command_list = [(tool, action, app) for (tool, app) in order]

		## build stored config
		self.config  = {tool : {config[tool][app].getName() : config[tool][app] for app in config[tool]} for tool in config}

	def runAction(self):
		for (tool, action, app) in self.command_list:
			tool_chain = self.tool_chains[tool]

			action = getattr(tool_chain, action)
			action(self.config[tool][app])

	def build(self, tools):
		print "Building"
		self.configure(tools, "build")
		self.runAction()

	def install(self, tools):
		print "Installing"
		self.configure(tools, "install")
		self.runAction()

	def document(self, tools):
		print "Documenting"
		self.configure(tools, "document")
		self.runAction()

	def clean(self, tools):
		print "Cleaning"
		self.configure(tools, "clean")
		self.runAction()

	def generate(self, tools):
		print "Generating"
		self.configure(tools, "generate")
		self.runAction()

	def link(self, tools):
		print "Linking"
		self.configure(tools, "link")
		self.runAction()

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

	fish                = FishMonger()

	tools_for_all       = fishmonger.InternalToolChains + fishmonger.ExternalToolChains
	
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
	actions["test"]     = [(None, [])]
	
	if cli[0] in actions:
		tasks = actions[cli[0]]
		for (task, tools) in tasks:
			task(tools)
	else:
		print "Usage: fishmonger <clean|build|compile|install|doc|document> [ToolChain[s]]"
		return 0

main()