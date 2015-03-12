import pybase.config
import pyerl       as PyErl
import pybase.util as PyUtil
import pybase.find as PyFind
import pyrcs       as PyRCS
import pybase.file as PyFile
import pybase.sh   as PySH
import os.path
import shutil

import fishmonger

class ToolChain(fishmonger.ToolChain):	
	## What follows is the fishmonger language api
	## All of the following variables and functions must be made available.
	
	## Generate language specific configuration
	## Return True if we are used, false if not
	def __init__(self):
		self.extensions = ["erl"]
		self.defaults   = {
		}

	def buildApp(self, child, app):
		includes = " "
		for include in app["INCLUDE_DIRS"]:
			if include == "":
				continue
			includes += "-I " + include + " "

		PySH.mkdirs(app.buildDir(subdir="ebin"))
		return ["erlc " + includes + "-o " + app.buildDir(subdir="ebin") + " " + os.path.join(app.srcDir(), "*.erl")]

	def installApp(self, child, app):
		## copy binaries
		install_erl_dir = app.installLangDir("erlang", subdir="ebin", app=True, version=True)
		PySH.copy(app.buildDir("ebin"), install_erl_dir, force=True)

