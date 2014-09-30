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

		print "JSCC", self.config["APP_CONFIG"]
		for app, app_dir, app_config in self.config["APP_CONFIG"]:
			src_dir = os.path.join(os.path.join(app_config["SRC_DIR"], app_dir), app_config["APP_SRC_DIR"])
			if not os.path.isdir(app_config["BUILD_DIR"]):
				os.makedirs(app_config["BUILD_DIR"])
			for js_file in PyDir.findFilesByExts(["js"], src_dir):
				target_file = os.path.join(app_config["BUILD_DIR"], js_file)
				print "JSCC_INCLUDE_DIRS=" + includes + " jscc " + os.path.join(src_dir, js_file) +  " > " + target_file
				PyUtil.shell("JSCC_INCLUDE_DIRS=" + includes + " jscc " + os.path.join(src_dir, js_file) +  " > " + target_file)

		return 0

	def install(self):
		install_dir = os.path.join(self.config["INSTALL_DIR"], "var/www/js")
		for app, app_dir, app_config in self.config["APP_CONFIG"]:
			app_install_dir = os.path.join(install_dir, app)
			if not os.path.isdir(app_install_dir):
				os.makedirs(app_install_dir)
			PyDir.copytree(app_config["BUILD_DIR"], os.path.join(install_dir, app))








