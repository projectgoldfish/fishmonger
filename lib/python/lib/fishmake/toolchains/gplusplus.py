import fishmake

class ToolChain(fishmake.ToolChain):
	def configure(self, app_config):
		self.config = app_config
		return False

	def compile(self):
		print "====> cxx"
		includes = " "
		for include in self.config.getDirs("INCLUDE_DIRS"):
			if include == "":
				continue
			includes += "-I " + include + " "
		pass