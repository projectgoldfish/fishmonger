import pybase.config
import pybase.sh   as PySH
import pybase.find as PyFind
import os.path

import fishmonger

class ToolChain(fishmonger.ToolChain):
	def __init__(self):
		self.defaults   = {
			"BUILD_DIR" : "js"
		}
		self.src_exts   = ["js"]
	
	def buildApp(self, app):
		includes = ".:${JSCC_INCLUDE_DIRS}"
		for include in app["INCLUDE_DIRS"]:
			if include == "":
				continue
			includes += ":" + include

		cmds = []
		for js_file in PyFind.findAllByExtensions(["js"], app.srcDir()):
			target_file = os.path.join(app.buildDir(), js_file)
			cmds.append("JSCC_INCLUDE_DIRS=" + includes + " jscc " + os.path.join(app.srcDir(), js_file) +  " > " + target_file)
		return cmds

	def installApp(self, app):
		for app in self.apps:
			app_install_dir = os.path.join(app.config["INSTALL_PREFIX"], "var/www/js/" + app.name)
			if not os.path.isdir(app_install_dir):
				os.makedirs(app_install_dir)
			PySH.copy(app.buildDir(), app_install_dir, force=True)

	def document(self):
		pass





