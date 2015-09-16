import fishmonger

class ToolChain(fishmonger.ToolChain):
	def __init__(self):
		self.src_exts   = ["java"]
		self.defaults   = {
			"DOC_DIR"  : "java"
		}