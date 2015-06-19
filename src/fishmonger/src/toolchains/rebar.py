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
		self.defaults = {
		}

	def uses(self, app):
		self.name()

		rebar_file = app.path(DF.source|DF.root, file_name="rebar.config")

		if os.path.isfile(rebar_file):
			return True
		return False

	def generate(self, app):
		pass

	def buildApp(self, child, app):
		return ["cd " + child.path(DF.source|DF.root) + " && rebar compile"]

	def link(self, app):
		pass

	def documentApp(self, child, app):
		for app in self.apps:
			PySH.cmd("cd " + app.appDir() + " && rebar doc")
			doc_dir = app.installDocDir("erlang")
			PySH.copy(app.appDir(subdir="doc"), doc_dir, force=True)

	def installApp(self, child, app):
		for dir in ["ebin", "priv"]:
			install_erl_dir = app.installLangDir("erlang", subdir=dir, app=True, version=True)
			PySH.copy(app.appDir(subdir=dir), install_erl_dir, force=True)
