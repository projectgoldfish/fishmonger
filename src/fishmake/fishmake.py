#! /usr/bin/python
import os
import fishmake
import pybase.config as PyConfig
import pybase.dir    as PyDir
import pybase.rcs    as PyRCS
import pybase.util   as PyUtil
import pybase.set    as PySet

class FishMake():
	def __init__(self, config={}, defaults={}):
		cli_config  = PyConfig.CLIConfig()
		sys_config  = PyConfig.SysConfig()
		self.config = PyConfig.Config()
		self.config.merge(defaults)
		self.config.merge(sys_config)
		self.config.merge(cli_config)
		self.config.merge(config)
		self.config.merge(PyConfig.FileConfig(".fishmake"))

		self.updated_repos = {}

	def retrieveCode(self, target, codebase):
		(name, url) = codebase
		target_dir = os.path.join(target, name)
		if self.config.get("SKIP_UPDATE", "False").upper() == "TRUE":
			return target_dir
		
		if name not in self.updated_repos:
			self.updated_repos[name] = True
			if not os.path.isdir(target_dir):
				print "==> Fetching:", name
				PyRCS.clone(url, target_dir)
			else:
				print "==> Updating:", name
				PyRCS.update(target_dir)
		return target_dir

	## We have to detect the applicaiton folders and generate base app
	## configurations here. Caling doConfigure will fill in the blanks.
	## Once we do that we can setup the tool chains
	def configure(self):
		## 0: For each src app
		##    0a: Checkout/update the src
		## 1: For each app
		##    1a: Generate an app config.
		##    1b: For each dependency
		##        1b1: Checkout/update the dependency
		## 2: Configure external toolchains.
		##    2a: Any app that is used by an external toolchain is to not
		##        be compiled by fishmake.
		## 3: Configure apps for tool chains
		## 4: Determine build order
		print "Configuring"
		app_dirs = ["."] + [self.retrieveCode(self.config.get("DEP_DIR", "dep"), codebase) for codebase in self.config.get("DEPENDENCIES", [])] + \
			PyDir.getDirDirs(self.config["SRC_DIR"])

		apps_byName = {}
		## For each app
		for app_dir in app_dirs:
			## Generate config
			t_appconfig = fishmake.AppConfig(app_dir)
			apps_byName[t_appconfig.name] = t_appconfig

			## For each dependency
			dep_dirs = [self.retrieveCode(self.config.get("DEP_DIR", "dep"), codebase) for codebase in t_appconfig.get("DEPENDENCIES", [])] + \
				PyDir.getDirDirs(os.path.join(app_dir, t_appconfig.config["SRC_DIR"]))
			for dep_dir in dep_dirs:
				if dep_dir in app_dirs:
					continue
				app_dirs.append(dep_dir)

		## Now that all code is checked out find the lib and include dirs
		self.config["LIB_DIRS"]     = self.config.getDirs("LIB_DIRS")     + PyDir.findDirsByName("lib")
		self.config["INCLUDE_DIRS"] = self.config.getDirs("INCLUDE_DIRS") + PyDir.findDirsByName("include")
		
		app_names     = apps_byName.keys()
		app_tcs       = {                 ## App Name -> ToolChains used
			name : PySet.Set() for name in app_names
		}               
		tc_apps       = {}                ## ToolChain.name -> App Names for apps build
		tcs_byName    = {}                ## String         -> ToolChain() mapping		
		t_apps_byName = dict(apps_byName) ## Copy made so we can alter it's state
		## Configure External ToolChains
		for ToolChains in [fishmake.ExternalToolChains, fishmake.InternalToolChains]:
			for t_tc in ToolChains:
				## Generate a tool chain instance.
				tc         = t_tc.ToolChain()
				tc_name    = tc.getName()
				## Get the list of apps this toolchain can build
				buildable_apps = tc.configure(self.config, t_apps_byName.values())

				## If the toolchain builds any apps
				if isinstance(buildable_apps, list) and buildable_apps != []:
					## Add it to the list of usable toolchains
					tcs_byName[tc_name] = tc
					
					## Store the apps this toolchain builds
					tc_apps[tc_name]    = buildable_apps

					for app_name in buildable_apps:
						## If we're configuring external toolchains then a match
						## indicats this app should not be available to other toolchains.
						if ToolChains == fishmake.ExternalToolChains:
							del t_apps_byName[app_name]

						## Store this tc in the app -> tc map
						app_tcs[app_name].add(tc_name)
		
		## We need to determine build order for tool chains.
		## Mapping toolchain -> prerequisite toolchains
		tc_priorities      = {x.name : PySet.Set(x.prerequisiteTools()) for x in tcs_byName.values()}
		## Mapping app -> prerequisite apps		
		app_priorities     = {x.name : PySet.Set(x.prerequisiteApps())  for x in apps_byName.values()}
		## Get tool chains that apps depend on 
		app_tcs_priorities = {name : PySet.Set() for name in app_names}

		## Generate mapping of app -> required toolchains
		for app_priority in app_priorities:
			## For each app that this app prioritizes	
			for app in app_priorities[app_priority]:
				## add the tool chains that that app uses
				app_tcs_priorities[app_priority].add(app_tcs[app])

		## We now know all tool chains that must be run before each app.
		## Some will have the toolchains they themselves used.
		## Since those chains cant be run before remove them from the mapping
		for app in app_tcs_priorities:
			app_tcs_priorities[app].remove(app_tcs[app])
	
		## We now have a mapping of app -> tcs that must be run before
		##   any of this app may by built.
		## Build out a map of all toolchains that must be run prior to
		##   other toolchains.
		## For each app
		for app_tcs_priority in app_tcs_priorities:
			## The toolchains that this app rely on must also be
			##   relied upon by the toolchains this app uses
			## For each toolchain that this app uses
			for tc in app_tcs[app_tcs_priority]:
				## Add the toolchains that this app relies on to the toolchain -> toolchain map
				tc_priorities[tc].add(app_tcs_priorities[app_tcs_priority])

		## We have the toolchain -> toolchain mapping
		##   Filter out the toolchains that we decided to skip.
		t_tc_priorities = dict(tc_priorities)

		for tc_name in tc_priorities:			
			## If BUILD_ONLY is set skip the unused toolchains
			tools_only = self.config.get("TOOLS_ONLY", [])
			if isinstance(tools_only, list):
				if tools_only == []:
					pass
				elif tc_name not in tools_only:
					del t_tc_priorities[tc_name]
			elif tools_only != tc_name:
				del t_tc_priorities[tc_name]

			## If BUILD_SKIP is set skip the specified toolchains
			tools_skip = self.config.get("TOOLS_SKIP", [])
			if isinstance(tools_skip, list):
				if tools_skip == []:
					pass
				elif tc_name in tools_skip:
					del t_tc_priorities[tc_name]
			elif tools_skip == tc_name:
				del t_tc_priorities[tc_name]

		tc_priorities    = t_tc_priorities
		tool_chain_order = PyUtil.determinePriority(tc_priorities)
		self.tool_chains = [tcs_byName[x] for x in tool_chain_order]

	def build(self):
		print "Building"
		for tool_chain in self.tool_chains:
			print "==>", tool_chain.name
			tool_chain.build()

	def install(self):
		print "Installing"
		for nix_dir in fishmake.NIXDirs:
			tnix_dir = PyDir.makeDirAbsolute(os.path.join(self.config.get("INSTALL_PREFIX", "install"), nix_dir))
			if not os.path.exists(tnix_dir):
				os.makedirs(tnix_dir)
		for tool_chain in self.tool_chains:
			print "==>", tool_chain.name
			tool_chain.install()

	def doc(self):
		print "Documenting"
		for tool_chain in self.tool_chains:
			print "==>", tool_chain.name
			tool_chain.doc()

def main():
	cli = PyConfig.CLIConfig()

	defaults = [
		("BUILD_DIR",      "build"),
		("SRC_DIR",        "src"),
		("INSTALL_PREFIX", "install"),
		("DOC_DIR",        "doc")
	]

	x = 1;
	extraToolChains = []
	while x in cli:
		extraToolChains.append(cli[x])
		x += 1

	fishmake.addInternalToolChains(extraToolChains)
	fishmake.addInternalToolChains(cli.get("INTERNAL_TOOLS", []))
	fishmake.addExternalToolChains(cli.get("EXTERNAL_TOOLS", []))

	fish = FishMake(**{"defaults" : defaults})
	fish.configure()
	if   cli[0] == "clean":
		return fish.clean()
	elif cli[0] == "build" or cli[0] == "compile":
		return fish.build()
	elif cli[0] == "install":
		return fish.install()
	elif cli[0] == "doc":
		return fish.doc()
	elif cli[0] == "test":
		return 0
	else:
		print "Usage: fishmake <clean|build|compile|install|doc> [ToolChain[s]]"
		return 0

main()