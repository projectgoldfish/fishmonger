import pybase.config
import pyerl       as PyErl
import pybase.sh   as PySH
import pybase.log  as PyLog
import os.path
import shutil

import fishmonger

class ToolChain(fishmonger.ToolChain):
	def __init__(self):
		self.extensions = ["erl"]
		self.defaults   = {}

	def documentApp(self, child, app):
		doc_dir = child.installDocDir("erlang")
		
		PySH.mkdirs(doc_dir)

		return ["erl -noshell -run edoc_run application '" + app.name() + "' '\"" + app.appDir() + "\"' '[{dir, \"" + doc_dir + "\"}]'"]
