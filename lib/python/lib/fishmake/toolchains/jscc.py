import pybase.config
import pybase.util as PyUtil
import pybase.dir as PyDir
import os.path

import fishmake

class ToolChain(fishmake.ToolChain):
	def configure(self, app_config):
		defaults = {
			"BUILD_DIR" : "js"
		}
		return self.doConfigure(file=".fishmake.jscc", extensions=["js"], app_config=app_config, defaults=defaults)

	def compile(self):
		includes = ".:${JSCC_INCLUDE_DIRS}"
		for include in self.config["INCLUDE_DIRS"]:
			if include == "":
				continue
			includes += ":" + include

		for app in self.apps:			
			if not os.path.isdir(app.buildDir()):
				os.makedirs(app.buildDir())
			for js_file in PyDir.findFilesByExts(["js"], app.srcDir()):
				target_file = os.path.join(app.buildDir(), js_file)
				print "JSCC_INCLUDE_DIRS=" + includes + " jscc " + os.path.join(app.srcDir(), js_file) +  " > " + target_file
				PyUtil.shell("JSCC_INCLUDE_DIRS=" + includes + " jscc " + os.path.join(app.srcDir(), js_file) +  " > " + target_file)

		return 0

	def install(self):
		for app in self.apps:
			app_install_dir = os.path.join(app.config["INSTALL_PREFIX"], "var/www/js/" + app.name)
			if not os.path.isdir(app_install_dir):
				os.makedirs(app_install_dir)
			PyDir.copytree(app.buildDir(), app_install_dir)

	def name(self):
		return "jscc"







