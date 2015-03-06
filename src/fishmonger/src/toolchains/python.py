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
		py_lib    = child.installLangSubDir("python", absolute=False)
		py_main   = child.installLangSubDir("python", file=child["APP_OPTIONS"]["PY_MAIN"], app=True, absolute=False)

		child_code  = "#! /bin/bash\n"
		child_code += "APP_ROOT=${APP_ROOT:-%s}\n" % child.installDir(absolute=True)
		child_code += "PYTHONPATH=${PYTHONPATH}:${APP_ROOT}/%s python ${APP_ROOT}/%s $@" % (py_lib, py_main)

		file_name = child.installBinDir(file=child.name())
		file      = PyFile.file(file_name, "w")
		file.write(child_code)
		file.close()

		PySH.cmd("chmod a+x %s" % file_name)

	def installLibrary(self, child):
		install_dir = child.installLangDir("python", app=True)

		PySH.copy(child.srcDir(), install_dir, pattern="*.py", force=True, root_only=True)
		