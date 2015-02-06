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
	def installApp(self, src_dir, app):
		self.installLibrary(src_dir, app)

		py_main = app.get("PY_MAIN", None)
		if py_main != None:
			self.installApplication(py_main, app)

	def installApplication(self, py_main, app):
		py_lib    = app.installDir(   prefix="lib/python/lib")
		py_main   = app.installAppDir(prefix="lib/python/lib", version=False, file=py_main)

		app_code  = "#! /bin/bash\n"
		app_code += "PYTHONPATH=${PYTHONPATH}:%s python %s $@" % (py_lib, py_main)

		file_name = app.installDir("bin", version=False, file=app.name)
		file      = PyFile.file(file_name, "w")
		file.write(app_code)
		file.close()

		PySH.cmd("chmod a+x %s" % file_name)

	def installLibrary(self, src_dir, app):
		install_dir = app.installAppDir(prefix="lib/python/lib", offset=src_dir, version=False)
		PySH.copy(src_dir, install_dir, pattern="*.py", force=True, root_only=True)
		