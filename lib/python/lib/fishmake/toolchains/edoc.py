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
	def configure(self, config):
		return self.do_configure(".fishmake.edoc", ["erl"], config)

	def compile(self):
		return 0

	def install(self):
		return 0

	def doc(self):
		print "==> Installing documentation..."
		for app in self.config["APP_CONFIG"]:
			doc_dir = app.installDir(os.path.join(app.config["DOC_DIR"], "erlang"))
			PyUtil.shell("erl -noshell -run edoc_run application '" + app.name + "' '\"" + app.appDir() + "\"' '[{dir, \"" + doc_dir + "\"}]'")
		print "==> Documentation installed!"