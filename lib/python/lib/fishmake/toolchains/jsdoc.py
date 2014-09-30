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
		defaults = {
			"BUILD_DIR" : "js"
		}
		return self.do_configure(".fishmake.jsdoc", ["js"], config, defaults)

	def compile(self):
		return 0

	def install(self):
		return 0

	def doc(self):
		doc_dir = os.path.join(self.config["INSTALL_DIR"], "doc/js")
		if not os.path.isdir(doc_dir):
			os.makedirs(doc_dir)

		print "==> Installing js documentation..."
		for app, app_dir, app_config in self.config["APP_CONFIG"]:
			print "===>", app
			src_dir    = os.path.join(os.path.join(app_config["SRC_DIR"], app_dir), app_config["BUILD_DIR"])

			print src_dir, PyDir.findFilesByExts(["js"], src_dir)


			target_dir = os.path.join(doc_dir, app + "-" + self.config["APP_VERSION"])
			target_files = ""
			for js_file in PyDir.findFilesByExts(["js"], src_dir):
				target_file = os.path.join(app_config["BUILD_DIR"], js_file)
				target_files += target_file + " "
			print "jsdoc -d " + target_dir + " " + target_files
			PyUtil.shell("jsdoc -d " + target_dir + " " + target_files)
		print "==> Documentation installed!"

