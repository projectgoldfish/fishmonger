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
		doc_dir = os.path.join(self.config["INSTALL_DIR"], "doc/erlang")
		if not os.path.isdir(doc_dir):
			os.makedirs(doc_dir)

		print "==> Installing erlang documentation...", 
		for app, app_dir, app_config in self.config["APP_CONFIG"]:
			print "===>", app
			target_dir = os.path.join(doc_dir, app + "-" + self.config["APP_VERSION"])
			PyUtil.shell("erl -noshell -run edoc_run application '" + app + "' '\"" + app_dir + "\"' '[{dir, \"" + target_dir + "\"}]'")
		print "==> Documentation installed!"

