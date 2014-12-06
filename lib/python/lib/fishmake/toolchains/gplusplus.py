import fishmake

class ToolChain(fishmake.ToolChain):
	def configure(self, app_config):
		defaults = {
			"BUILD_DIR"  : "lib",
			"EXECUTABLE" : "false"
		}
		return self.doConfigure(file=".fishmake.g++", extensions=["c", "cpp"], defaults=defaults, app_config=app_config)

	def buildCommands(self, app):
		pass

	def name(self):
		return "g++"