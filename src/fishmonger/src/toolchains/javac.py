import fishmonger
import fishmonger.config    as FC
import fishmonger.dirflags  as DF
import fishmonger.utils.jvm as JVM

import pybase.sh            as PySH

class ToolChain(fishmonger.ToolChain):
	def __init__(self):
		self.extensions = ["java"]
		self.defaults   = {
			"DOC_DIR"  : "java"
		}

	def buildApp(self, child, app):
		## We want to build all java files at once.
		## Ignore and subdirs

		if child.type != FC.AppToolConfig.Types.app:
			return []

		class_path  = JVM.getSourceClassPath([app] + app.children)
		class_files = JVM.getSourceFiles([app] + app.children)
		build_path  = child.path(DF.build|DF.langlib|DF.app, lang="java")

		PySH.mkdirs(build_path)

		files = ""
		for f in class_files:
			files += f + " "

		return ["javac -cp \"" + class_path + "\" -d " + build_path + " " + files]

	def installApp(self, child, app):
		pass

