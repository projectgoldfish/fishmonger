import pybase.config
import pyerl       as PyErl
import pybase.util as PyUtil
import pybase.dir  as PyDir
import os.path
import shutil

import fishmake

class ToolChain(fishmake.ToolChain):
	def __init__(self):
		self.extensions = ["erl"]

	def build(self):
		pass

	def install(self):
		pass

	def installDoc(self, app):
		doc_dir = app.installDocDir("erlang")
		if os.path.isdir(doc_dir):
			shutil.rmtree(doc_dir)
			os.makedirs(doc_dir)

		PyUtil.shell("erl -noshell -run edoc_run application '" + app.name + "' '\"" + app.appDir() + "\"' '[{dir, \"" + doc_dir + "\"}]'", prefix="======>", stdout=True, stderr=True)
