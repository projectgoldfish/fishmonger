import pybase.config
import pyerl       as PyErl
import pybase.util as PyUtil
import pybase.dir  as PyDir
import os.path
import shutil

import fishmake

class ToolChain(fishmake.ToolChain):
	def __init__(self):
		pass

	## Generate language specific configuration
	## Return True if we are used, false if not
	def configure(self, fish_config, app_configs):
		apps = []
		for config in app_configs:
			if os.path.isfile(os.path.join(config.appDir(), "rebar.config")):
				apps.append(config)

		self.apps = apps
		## If apps is [] we do not need this tool chain
		return [app.name for app in self.apps]

	def buildCommands(self, app):
		return ["cd " + app.appDir() + " && rebar compile"]

	def doc(self):
		for app in self.apps:
			PyUtil.shell("cd " + app.appDir() + " && rebar doc")
			doc_dir = app.installDocDir("erlang")
			PyDir.copytree(os.path.join(app.appDir(), "doc"), doc_dir, force=True)

	def install(self):
		for app in self.apps:
			install_erl_dir = app.installAppDir("lib/erlang/lib")
			for dir in ["priv", "ebin"]:
				install_source = os.path.join(app.appDir(), dir)
				install_target = os.path.join(install_erl_dir, dir)
				if os.path.isdir(install_source):
					PyDir.copytree(install_source, install_target, force=True)