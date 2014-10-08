import pybase.config
import pyerl       as PyErl
import pybase.util as PyUtil
import pybase.dir  as PyDir
import os.path
import shutil

import fishmake

class ToolChain(fishmake.ToolChain):
	## Generate language specific configuration
	## Return True if we are used, false if not
	def configure(self, app_config):
		print "Configuring rebar"
		apps = []
		for config in app_config:
			if os.path.isfile(os.path.join(config.appDir(), "rebar.config")):
				apps.append(config)

		self.apps = apps
		## If apps is [] we do not need this tool chain
		return apps != []

	def compile(self):
		print "=> rebar"
		for app in self.apps:
			PyUtil.shell("cd " + app.appDir() + " && rebar compile")

	def doc(self):
		for app in self.apps:
			PyUtil.shell("cd " + app.appDir() + " && rebar doc")
			doc_dir = app.installVersionDir(os.path.join(app.config["DOC_DIR"], "erlang"))
			if os.path.exists(doc_dir):
				PyUtil.shell("rm -rf " + doc_dir)
			os.makedirs(doc_dir)
			PyDir.copytree(os.path.join(app.appDir(), "doc"), doc_dir)

	def install(self):
		for app in self.apps:
			install_erl_dir = app.installVersionDir("lib/erlang/lib")
			if os.path.exists(install_erl_dir):
				PyUtil.shell("rm -rf " + install_erl_dir)
			for dir in ["priv", "ebin"]:
				install_target = os.path.join(install_erl_dir, dir)
				if os.path.isdir(os.path.join(app.appDir(), dir)):
					os.makedirs(install_target)
					PyDir.copytree(os.path.join(app.appDir(), dir), install_target)
		