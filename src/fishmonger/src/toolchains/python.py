import os.path

import pybase.config
import pybase.find as PyFind
import pybase.file as PyFile
import pybase.log  as PyLog
import pybase.sh   as PySH

import fishmonger
import fishmonger.dirflags as DF

import traceback

class ToolChain(fishmonger.ToolChain):
	def __init__(self):
		self.defaults   = {
			"APPLICATION" : False
		}
		self.extensions = ["py"]

	def installApp(self, child, app):
		self.installLibrary(child)

		if "PY_MAIN" in child["APP_OPTIONS"] and child.isRoot():
			self.installApplication(child)

	def installApplication(self, child):
		install_dir = child.path(DF.install|DF.root|DF.absolute)
		py_lib      = child.path(DF.install|DF.langlib|DF.relative,        lang="python", relative_to=install_dir)
		py_main     = child.path(DF.install|DF.langlib|DF.app|DF.relative, lang="python", relative_to=install_dir, file_name=child["APP_OPTIONS"]["PY_MAIN"])

		child_code  = "#! /bin/bash\n"
		child_code += "APP_ROOT=${APP_ROOT:-%s}\n" % install_dir
		child_code += "PYTHONPATH=${PYTHONPATH}:${APP_ROOT}/%s python ${APP_ROOT}/%s $@" % (py_lib, py_main)

		file_name = child.path(DF.install|DF.bin, file_name=child.name())
		file      = PyFile.file(file_name, "w")
		file.write(child_code)
		file.close()

		PySH.cmd("chmod a+x %s" % file_name)

	def installLibrary(self, child):
		install_dir = child.path(DF.install|DF.langlib|DF.app, lang="python")
		source_dir  = child.path(DF.source|DF.src)

		PyLog.debug("Copy " + source_dir + " -> " + install_dir, log_level=6)

		PySH.copy(source_dir, install_dir, pattern="*.py", force=True, root_only=True)
		