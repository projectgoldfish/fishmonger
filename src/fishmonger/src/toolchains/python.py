import fishmonger
import fishmonger.toolchains

import pybase.log as PyLog

class ToolChain(fishmonger.toolchains.ToolChain):
	def srcExts(self):
		return ["py"]

	def compile(self, app_dir, config):
		PyLog.log("Running")

		app_dir.copy(config["build_dir"], pattern="*.py")

		return None

	def install(self, app_dir, config):
		pass