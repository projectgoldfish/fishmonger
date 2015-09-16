import pybase.sh   as PySH
import pybase.find as PyFind
import pybase.path as PyPath
import os.path

import fishmonger

class ToolChain(fishmonger.ToolChain):
	def __init__(self):
		self.src_exts   = ["java"]
		self.defaults   = {
			"DOC_DIR"  : "java"
		}

	def documentApp(self, app):
		doc_dir = app.installDocDir("java")

		if os.path.isdir(doc_dir):
			shutil.rmtree(doc_dir)
		os.makedirs(doc_dir)

		java_files = ""
		for java_file in PyFind.findAllByExts(["java"], app.srcDir()):
			java_files += java_file + " "

		return ["javadoc -classpath " + classpath + " -d " + doc_dir + " " + target_files]