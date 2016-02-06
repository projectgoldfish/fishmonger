import fishmonger
import fishmonger.toolchains


class ToolChain(fishmonger.toolchains.ToolChain):
	def srcExts(self):
		return ["py"]

	def build(self, app_dir, config):
		pass