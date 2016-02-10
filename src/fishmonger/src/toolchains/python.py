import fishmonger
import fishmonger.toolchains

import pybase.log as PyLog

class ToolChain(fishmonger.toolchains.ToolChain):
	def srcExts(self, stage):
		exts = {
			"compile" : ["py"]
		}
		return exts.get(stage, [])

	def compile(self, app_dir, config, src_files):
		PyLog.log("Running")

		app_dir.copy(config["build_dir"], pattern="*.py")

		return None

	def install(self, app_dir, config, src_files):
		pass