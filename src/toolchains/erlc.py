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

class ToolChain(fishmonger.toolchains.ToolChain):	
	def exts(self):
		return {
			"build"   : ["erl",  "app.src"],
			"install" : ["beam", "app"]
		}

	def build(self, app_dir, config, src_files):
		includes = " "
		for include in app["INCLUDE_DIRS"]:
			if include == "":
				continue
			includes += "-I " + include + " "

		build_dir = app.path(DF.build|DF.langlib|DF.app, lang="erlang", subdirs=["ebin"])
		PySH.mkdirs(build_dir)
		return ["erlc " + includes + "-o " + build_dir + " " + app.path(DF.source|DF.src, file_name="*.erl")]

	def installFiles(self, app_dir, config):
		return self._usedFiles(app_dir.langlib("python", config["build_dir"]), self.exts()["install"])

	def install(self, app_dir, config, src_files):
		## copy binaries
		install_erl_dir = app.path(DF.install|DF.langlib|DF.app|DF.version, lang="erlang", subdirs=["ebin"])
		PySH.copy(app.path(DF.build|DF.langlib|DF.app, lang="erlang", subdirs=["ebin"]), install_erl_dir, force=True)

		build_dir   = self.langlibFile(app_dir, app_dir, "erlang", config["build_dir"])
		install_dir = self.langlibFile(app_dir, app_dir, "erlang", config["install_dir"])
		for f in src_files:
			print f, "->", install_dir.join(f.relative(build_dir))
			#f.copy(self.langlibFile(app_dir, f, "python", config["install_dir"]))
		return None	