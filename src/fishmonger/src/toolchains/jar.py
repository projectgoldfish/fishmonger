import pybase.config
import pybase.sh   as PySH
import pybase.find as PyFind
import os.path

import fishmonger

class ToolChain(fishmonger.ToolChain):
	def __init__(self):
		self.extensions = ["class"]
		self.defaults   = {
			"BUILD_DIR"  : "js"
		}