import pybase.config
import pyerl       as PyErl
import pybase.log  as PyLog
import pybase.sh   as PySH
import pybase.find as PyFind
import os.path
import shutil

import fishmonger

class ToolChain(fishmonger.ToolChain):
	## Generate language specific configuration
	## Return True if we are used, false if not

	def __init__(self):
		self.src_exts   = ["js"]
		self.defaults   = {
		}

	def documentApp(self, app):
		doc_dir = app.installDocDir("js")

		if os.path.isdir(doc_dir):
			shutil.rmtree(doc_dir)
		os.makedirs(doc_dir)

		target_files = ""
		for js_file in PyFind.findAllByPattern("*.js", app.srcDir()):
			target_file = os.path.join(app.srcDir(), js_file)
			target_files += target_file + " "

		PySH.cmd("jsdoc -d " + doc_dir + " " + target_files, prefix=PyLog.indent, stdout=True, stderr=True)