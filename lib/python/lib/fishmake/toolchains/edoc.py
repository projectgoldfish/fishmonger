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

	def buildCommands(self, app):
		doc_dir = os.path.join(app.appDir(), app.config["DOC_DIR"] + "-edoc")
		return ["erl -noshell -run edoc_run application '" + app.name + "' '\"" + app.appDir() + "\"' '[{dir, \"" + doc_dir + "\"}]'"]

	def installApp(self, app):
		src_dir = os.path.join(app.appDir(), app.config["DOC_DIR"])
		doc_dir = app.installVersionDir(os.path.join(app.config["DOC_DIR"], "erlang"))

		os.makedirs(doc_dir)

		PyDir.copytree(src_dir, doc_dir)

	def name(self):
		return "edoc"