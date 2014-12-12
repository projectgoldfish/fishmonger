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
		defaults = {
			"BUILD_DIR" : "js"
		}
		return self.doConfigure(file=".fishmake.jsdoc", extensions=["js"], app_config=app_config, defaults=defaults)

	def buildCommands(self, app):
		target_dir = os.path.join(app.appDir(), app.config["DOC_DIR"] + "-jsdoc")
		target_files = ""
		for js_file in PyDir.findFilesByExts(["js"], app.buildDir()):
			target_file = os.path.join(app.buildDir(), js_file)
			target_files += target_file + " "

		return ["jsdoc -d " + target_dir + " " + target_files]

	def installApp(self, app):
		src_dir = os.path.join(app.appDir(), app.config["DOC_DIR"] + "-jsdoc")
		doc_dir = app.installVersionDir(os.path.join(app.config["DOC_DIR"], "js"))

		os.makedirs(doc_dir)

		PyDir.copytree(src_dir, doc_dir)

	def name(self):
		return "jsdoc"