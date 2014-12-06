import fishmake

class ToolChain(fishmake.ToolChain):
	def configure(self, config):
		return False

	def name(self):
		return "fishmake"

	def buildCommands(self, app):
		pass
