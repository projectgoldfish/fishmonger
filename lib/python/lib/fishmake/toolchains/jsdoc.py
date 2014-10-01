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
		print "==> Installing js documentation..."
		for app in self.config["APP_CONFIG"]:
			print "===>", app.name
			
			target_dir = app.installDir(os.path.join(app.config["DOC_DIR"], "js"))
			target_files = ""
			for js_file in PyDir.findFilesByExts(["js"], app.buildDir()):
				target_file = os.path.join(app.buildDir(), js_file)
				target_files += target_file + " "
			PyUtil.shell("jsdoc -d " + target_dir + " " + target_files)
		print "==> Documentation installed!"

