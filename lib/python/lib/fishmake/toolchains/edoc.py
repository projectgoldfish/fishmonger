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

	def doc(self):
		print "==> Installing documentation..."
		for app in self.apps:
			doc_dir = app.installVersionDir(os.path.join(app.config["DOC_DIR"], "erlang"))
			PyUtil.shell("erl -noshell -run edoc_run application '" + app.name + "' '\"" + app.appDir() + "\"' '[{dir, \"" + doc_dir + "\"}]'")
		print "==> Documentation installed!"

	def name(self):
		return "edoc"