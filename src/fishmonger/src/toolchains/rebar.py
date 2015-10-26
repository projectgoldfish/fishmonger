import pybase.config as PC
import pyerl         as PyErl
import pybase.util   as PyUtil
import pybase.find   as PyFind
import pybase.sh     as PySH
import os.path
import shutil

import fishmonger
import fishmonger.dirflags as DF

class ToolChain(fishmonger.ToolChain):
	def __init__(self):
		self.src_exts = ["erl"]
		self.defaults = {
		}

	def uses(self, app):
		self.name()

		rebar_file = app.path(DF.source|DF.root, file_name="rebar.config")

		if os.path.isfile(rebar_file):
			return True
		return False

	def generate(self, app):
		return True

	def link(self, app):
		return True

	def buildApp(self, child, app):
		return [
			"cd {0} && rebar get-deps".format(child.path(DF.source|DF.root)),
			"cd {0} && rebar compile".format(child.path(DF.source|DF.root))
		]

	def documentApp(self, child, app):
		for app in self.apps:
			PySH.cmd("cd " + app.path(DF.source|DF.root) + " && rebar doc")
			doc_dir = app.path(DF.install|DF.doc|DF.app|DF.version, dirs=["erlang"])
			PySH.copy(app.path(DF.source|DF.root, subdir="doc"), doc_dir, force=True)

	def installApp(self, child, app):
		app_root     = app.path(DF.source|DF.root)
		dep_roots    = PyFind.getDirDirs(os.path.join(app_root, "deps"))

		for dir in ["ebin", "priv"]:
			install_erl_dir = app.path(DF.install|DF.langlib|DF.app|DF.version, lang="erlang", subdirs=[dir])
			PySH.copy(app.path(DF.source|DF.root, subdirs=[dir]), install_erl_dir, force=True)

		for (dep_name, dep_dir) in [(os.path.basename(d_root), d_root) for d_root in dep_roots]:
			for dir in ["ebin", "priv"]:
				install_erl_dir = app.path(DF.install|DF.langlib|DF.app|DF.version, lang="erlang", subdirs=[dir], dep_name=dep_name, dep_dir=dep_dir)
				PySH.copy(os.path.join(dep_dir, dir), install_erl_dir, force=True)

