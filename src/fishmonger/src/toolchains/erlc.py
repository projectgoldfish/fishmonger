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
			"BUILD_DIR"  : "ebin",
			"EXECUTABLE" : "false"
		}

	def buildApp(self, src_dir, app):
		print "BUILD"
		includes = " "
		for include in app["INCLUDE_DIRS"]:
			if include == "":
				continue
			includes += "-I " + include + " "

		return ["erlc " + includes + "-o " + app.buildDir() + " " + os.path.join(app.srcDir(), "*.erl")]

	def installApp(self, app):
		## copy binaries
		install_erl_dir = app.installAppDir("lib/erlang/lib")
		install_target  = os.path.join(install_erl_dir, "ebin")
		PySH.copy(app.appDir("ebin"), install_target, force=True)


	def document(self):
		pass
