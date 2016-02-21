import fishmonger
import fishmonger.path       as FishPath
import fishmonger.toolchains

import pybase.log as PyLog

class ToolChain(fishmonger.toolchains.ToolChain):
	def exts(self):
		return {
			"build"   : ["py"]
		}

	def build(self, app_dir, config, src_files):
		for f in src_files:
			f.copy(self.langlibFile(app_dir, f, "python", config["build_dir"]))
		return None

	def installFiles(self, app_dir, config):
		return self._usedFiles(app_dir.langlib("python", config["build_dir"]), self.exts()["build"])

	def install(self, app_dir, config, src_files):
		for f in src_files:
			f.copy(self.langlibFile(app_dir, f, "python", config["install_dir"]))
		return None
