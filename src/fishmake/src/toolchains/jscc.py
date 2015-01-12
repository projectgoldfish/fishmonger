import pybase.config
import pybase.util as PyUtil
import pybase.dir as PyDir
import os.path

import fishmake

class ToolChain(fishmake.ToolChain):
	def __init__(self):
		self.defaults   = {
			"BUILD_DIR" : "js"
		}
		self.extensions = ["js"]
	
	def buildCommands(self, app):
		includes = ".:${JSCC_INCLUDE_DIRS}"
		for include in app["INCLUDE_DIRS"]:
			if include == "":
				continue
			includes += ":" + include

		cmds = []
		for js_file in PyDir.findFilesByExts(["js"], app.srcDir()):
			target_file = os.path.join(app.buildDir(), js_file)
			cmds.append("JSCC_INCLUDE_DIRS=" + includes + " jscc " + os.path.join(app.srcDir(), js_file) +  " > " + target_file)
		return cmds

	def installApp(self, app):
		for app in self.apps:
			app_install_dir = os.path.join(app.config["INSTALL_PREFIX"], "var/www/js/" + app.name)
			if not os.path.isdir(app_install_dir):
				os.makedirs(app_install_dir)
			PyDir.copytree(app.buildDir(), app_install_dir, force=True)

	def doc(self):
		pass





