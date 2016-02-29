import fishmonger
import fishmonger.path       as FishPath
import fishmonger.toolchains

import pybase.log as PyLog

class ToolChain(fishmonger.toolchains.LibToolChain):
	def exts(self):
		return {
			"build"   : ["py"]
		}
