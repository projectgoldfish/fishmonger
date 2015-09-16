import fishmonger

class ToolChain(fishmonger.ToolChain):
	def __init__(self):
		self.src_exts   = ["c", "cpp"]
		self.defaults   = {
			"BUILD_DIR"  : "lib",
			"EXECUTABLE" : "false"
		}

	def buildCommands(self, app):
		pass
