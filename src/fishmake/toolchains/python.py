import pybase.config
import pybase.util as PyUtil
import pybase.dir as PyDir
import os.path

import re

import fishmake

class ToolChain(fishmake.ToolChain):
	def __init__(self):
		self.defaults   = {
			"APPLICATION" : False
		}
		self.extensions = ["py"]
	
	## Nothing to build for python
	def build(self):
		pass

	## 
	def installApp(self, app):
		if app.get("APPLICATION") == True:
			self.installApplication(app)
		else:
			self.installLibrary(app)

	def doc(self):
		pass

	def installLibrary(self, app):
		install_dir = app.installAppDir("lib/python/lib", version=False)
		PyDir.copytree(app.srcDir(), install_dir, pattern="^(.*)\.py$", force=True)
		