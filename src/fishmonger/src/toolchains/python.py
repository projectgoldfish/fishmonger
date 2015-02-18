import os.path

import pybase.config
import pybase.find as PyFind
import pybase.file as PyFile
import pybase.sh   as PySH

import fishmonger

import traceback

class ToolChain(fishmonger.ToolChain):
	def __init__(self):
		self.defaults   = {
			"APPLICATION" : False
		}
		self.extensions = ["py"]

	## 
	def installApp(self, app):
		self.installLibrary(app)

		if "PY_MAIN" in app["APP_OPTIONS"] and app.isRoot():
			self.installApplication(app)

	def installApplication(self, app):
		py_lib    = app.installLangDir("python", absolute=True)
		py_main   = app.installLangDir("python", file=app["APP_OPTIONS"]["PY_MAIN"], app=True, absolute=True)

		app_code  = "#! /bin/bash\n"
		app_code += "PYTHONPATH=${PYTHONPATH}:%s python %s $@" % (py_lib, py_main)

		file_name = app.installBinDir(file=app.name())
		file      = PyFile.file(file_name, "w")
		file.write(app_code)
		file.close()

		PySH.cmd("chmod a+x %s" % file_name)

	def installLibrary(self, app):
		install_dir = app.installLangDir("python", app=True)

		PySH.copy(app.srcDir(), install_dir, pattern="*.py", force=True, root_only=True)
		