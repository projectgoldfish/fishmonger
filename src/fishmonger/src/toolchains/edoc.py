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

	def documentApp(self, app):
		doc_dir = app.installDocDir("erlang")
		if os.path.isdir(doc_dir):
			shutil.rmtree(doc_dir)
		os.makedirs(doc_dir)

		PySH.cmd("erl -noshell -run edoc_run application '" + app.name() + "' '\"" + app.appDir() + "\"' '[{dir, \"" + doc_dir + "\"}]'", prefix=PyLog.indent, stdout=True, stderr=True)
