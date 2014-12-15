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
		return self.doConfigure(file=".fishmake.edoc", extensions=["erl"], app_config=app_config)

	def build(self):
		pass

	def install(self):
		pass

	def installDoc(self, app):
		doc_dir = app.installDocDir("erlang")
		if os.path.isdir(doc_dir):
			shutil.rmtree(doc_dir)
			os.makedirs(doc_dir)

		PyUtil.shell("erl -noshell -run edoc_run application '" + app.name + "' '\"" + app.appDir() + "\"' '[{dir, \"" + doc_dir + "\"}]'", prefix="======>", stdout=True, stderr=True)

	def name(self):
		return "edoc"