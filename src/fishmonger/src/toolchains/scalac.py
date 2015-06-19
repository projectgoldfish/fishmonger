import fishmonger.utils.jvm as JVM
import fishmonger

class ToolChain(fishmonger.ToolChain):
	def __init__(self):

		print "SCAVAC"

		self.extensions = ["scala"]
		self.defaults   = {
			"DOC_DIR"  : "scala"
		}

	def buildApp(self, child, app):
		CP = JVM.getClassPath(self.apps)

		print "ClassPath", CP

	def installApp(self, child, app):
		pass

