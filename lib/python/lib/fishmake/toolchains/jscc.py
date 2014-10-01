from   pybase.config import GlobalConfig as PyConfig
import pybase.config
import pybase.util as PyUtil
import pybase.dir as PyDir
import os.path

import fishmake

def configFile():
	return ".fishmake.js"

def getFileTypes():
	return ["js"]

def compile(path):
	print "====> js"
	includes = " "
	for include in PyConfig["INCLUDE_DIRS"]:
		if include == "":
			continue
		includes += "-I " + include + " "

	return 0

def install(path):
	
	pass

def doc(path):
	pass

class ToolChain(fishmake.ToolChain):
	def __init__(self):
		pass

	def configure(self, config):
		defaults = {
			"BUILD_DIR" : "js"
		}
		return self.do_configure(".fishmake.jscc", ["js"], config, defaults)

	def compile(self):
		#JSCC_INCLUDE_DIRS=.:${JSCC_INCLUDE_DIRS}:jsrc/include jscc ${FISHOS_SRC}/fishos.js > ${FISHOS_OUT}/fishos.js
		includes = ".:${JSCC_INCLUDE_DIRS}"
		for include in self.config["INCLUDE_DIRS"]:
			if include == "":
				continue
			includes += ":" + include

		for app in self.config["APP_CONFIG"]:			
			if not os.path.isdir(app.buildDir()):
				os.makedirs(app.buildDir())
			for js_file in PyDir.findFilesByExts(["js"], app.srcDir()):
				target_file = os.path.join(app.buildDir(), js_file)
				print "JSCC_INCLUDE_DIRS=" + includes + " jscc " + os.path.join(app.srcDir(), js_file) +  " > " + target_file
				PyUtil.shell("JSCC_INCLUDE_DIRS=" + includes + " jscc " + os.path.join(app.srcDir(), js_file) +  " > " + target_file)

		return 0

	def install(self):
		for app in self.config["APP_CONFIG"]:
			app_install_dir = os.path.join(app.config["INSTALL_PREFIX"], "var/www/js/" + app.name)
			if not os.path.isdir(app_install_dir):
				os.makedirs(app_install_dir)
			PyDir.copytree(app.buildDir(), app_install_dir)








