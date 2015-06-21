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
import fishmonger.dirflags as DF

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

		build_dir = app.path(DF.build|DF.langlib|DF.app, lang="erlang", subdirs=["ebin"])
		PySH.mkdirs(build_dir)
		return ["erlc " + includes + "-o " + build_dir + " " + app.path(DF.source|DF.src, file_name="*.erl")]

	def installApp(self, child, app):
		## copy binaries
		install_erl_dir = app.path(DF.install|DF.langlib|DF.app|DF.version, lang="erlang", subdirs=["ebin"])
		PySH.copy(app.path(DF.build|DF.langlib|DF.app, lang="erlang", subdirs=["ebin"]), install_erl_dir, force=True)

