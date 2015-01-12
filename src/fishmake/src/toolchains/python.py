import pybase.config
import pybase.util as PyUtil
import pybase.dir as PyDir
import os.path

import re

import fishmake

class ToolChain(fishmake.ToolChain):
	def __init__(self):
		self.defaults   = {
			"APPLICATION" : False
		}
		self.extensions = ["py"]
	
	## Nothing to build for python
	def build(self):
		pass

	## 
	def installApp(self, app):
		self.installLibrary(app)

		py_main = app.get("PY_MAIN", None)
		if py_main != None:
			self.installApplication(py_main, app)
			

	def doc(self):
		pass

	def installApplication(self, py_main, app):
		py_lib    = PyDir.makeDirAbsolute(app.installDir("lib/python/lib"))
		py_main   = os.path.join(app.installAppDir("lib/python/lib", version=False), py_main)

		app_code  = "#! /bin/bash\n"
		app_code += "PYTHONPATH=${PYTHONPATH}:%s python %s $@" % (py_lib, py_main)

		file_name = app.installAppDir("bin", version=False)
		file      = open(file_name, "w")
		file.write(app_code)
		file.close()

		PyUtil.shell("chmod a+x %s" % file_name)

	def installLibrary(self, app):
		install_dir = app.installAppDir("lib/python/lib", version=False)
		PyDir.copytree(app.srcDir(), install_dir, pattern="^(.*)\.py$", force=True)
		