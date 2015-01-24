import fishmonger

class ToolChain(fishmonger.ToolChain):
	def __init__(self):
		self.extensions = ["c", "cpp"]
		self.defaults   = {
			"BUILD_DIR"  : "lib",
			"EXECUTABLE" : "false"
		}

	def buildCommands(self, app):
		pass
