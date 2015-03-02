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
	def installApp(self, child, app):
		self.installLibrary(child)

		if "PY_MAIN" in child["APP_OPTIONS"] and child.isRoot():
			self.installApplication(child)

	def installApplication(self, child):
		py_lib    = child.installLangDir("python", absolute=True)
		py_main   = child.installLangDir("python", file=child["APP_OPTIONS"]["PY_MAIN"], app=True, absolute=True)

		child_code  = "#! /bin/bash\n"
		child_code += "PYTHONPATH=${PYTHONPATH}:%s python %s $@" % (py_lib, py_main)

		file_name = child.installBinDir(file=child.name())
		file      = PyFile.file(file_name, "w")
		file.write(child_code)
		file.close()

		PySH.cmd("chmod a+x %s" % file_name)

	def installLibrary(self, child):
		install_dir = child.installLangDir("python", app=True)

		PySH.copy(child.srcDir(), install_dir, pattern="*.py", force=True, root_only=True)
		