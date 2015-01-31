import fishmonger

class ToolChain(fishmonger.ToolChain):
	def __init__(self):
		self.extensions = ["java"]
		self.defaults   = {
			"DOC_DIR"  : "java"
		}