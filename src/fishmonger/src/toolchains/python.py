import os.path

import pybase.config
import pybase.find as PyFind
import pybase.file as PyFile
import pybase.log  as PyLog
import pybase.sh   as PySH

import fishmonger
import fishmonger.dirflags as DF

class ToolChain(fishmonger.ToolChain):
	def __init__(self):
		self.defaults   = {
			"APPLICATION" : False
		}
		self.src_exts   = ["py"]

	def buildApp(self, child, app):
		self.buildLibrary(child)

		if "PY_MAIN" in child["APP_OPTIONS"] and child.isRoot():
			PyLog.log("application script")
			PyLog.increaseIndent()
			self.buildApplication(child)
			PyLog.decreaseIndent()

	def buildApplication(self, child):
		build_dir      = child.path(DF.build|DF.root|DF.absolute)
		py_lib         = child.path(DF.build|DF.langlib|DF.relative, lang="python", relative_to=build_dir)
		py_main        = child.path(DF.source|DF.src, file_name=child["APP_OPTIONS"]["PY_MAIN"])
		
		script_name    = child["APP_OPTIONS"]["PY_MAIN"] if child["APP_OPTIONS"]["PY_MAIN"] != "main.py" else child.name() + "-main.py"
		py_main_use    = child.path(DF.build|DF.langlib,             lang="python", subdirs=["apps"], relative_to=build_dir, file_name=script_name)
		py_main_script = child.path(DF.build|DF.langlib|DF.relative, lang="python", subdirs=["apps"], relative_to=build_dir, file_name=script_name)

		PySH.copy(py_main, py_main_use, dst_type="file", force=True)

		child_code  = "#! /bin/bash\n"
		child_code += "APP_ROOT=${APP_ROOT:-%s}\n" % build_dir
		child_code += "PYTHONPATH=${PYTHONPATH}:${APP_ROOT}/%s python ${APP_ROOT}/%s $@" % (py_lib, py_main_script)

		file_name   = child.path(DF.build|DF.bin, file_name=child.name())
		file        = PyFile.file(file_name, "w")
		file.write(child_code)
		file.close()

		PySH.cmd("chmod a+x %s" % file_name)

	def buildLibrary(self, child):
		build_dir  = child.path(DF.build|DF.langlib|DF.app, lang="python")
		source_dir = child.path(DF.source|DF.src)

		PyLog.debug("Copy " + source_dir + " -> " + build_dir, log_level=6)

		PySH.copy(source_dir, build_dir, pattern="*.py", force=True, root_only=True)
				
	def installApp(self, child, app):
		self.installLibrary(child)

		if "PY_MAIN" in child["APP_OPTIONS"] and child.isRoot():
			PyLog.log("application script")
			PyLog.increaseIndent()
			self.installApplication(child)
			PyLog.decreaseIndent()

	def installLibrary(self, child):
		build_dir   = child.path(DF.build|DF.langlib|DF.app,   lang="python")
		install_dir = child.path(DF.install|DF.langlib|DF.app, lang="python")

		PyLog.debug("Copy " + build_dir + " -> " + install_dir, log_level=6)

		PySH.copy(build_dir, install_dir, pattern="*.py", force=True, root_only=True)

	def installApplication(self, child):
		install_dir    = child.path(DF.install|DF.root|DF.absolute)
		py_lib         = child.path(DF.install|DF.langlib|DF.relative, lang="python", relative_to=install_dir)
		
		script_name    = child["APP_OPTIONS"]["PY_MAIN"] if child["APP_OPTIONS"]["PY_MAIN"] != "main.py" else child.name() + "-main.py"
		py_main        = child.path(DF.build|DF.langlib,               lang="python", subdirs=["apps"], file_name=script_name)
		py_main_use    = child.path(DF.install|DF.langlib,             lang="python", subdirs=["apps"], file_name=script_name)
		py_main_script = child.path(DF.install|DF.langlib|DF.relative, lang="python", subdirs=["apps"], relative_to=install_dir, file_name=script_name)

		PySH.copy(py_main, py_main_use, dst_type="file", force=True)

		child_code  = "#! /bin/bash\n"
		child_code += "APP_ROOT=${APP_ROOT:-%s}\n" % install_dir
		child_code += "PYTHONPATH=${PYTHONPATH}:${APP_ROOT}/%s python ${APP_ROOT}/%s $@" % (py_lib, py_main_script)

		file_name   = child.path(DF.install|DF.bin, file_name=child.name())
		file        = PyFile.file(file_name, "w")
		file.write(child_code)
		file.close()

		PySH.cmd("chmod a+x %s" % file_name)
