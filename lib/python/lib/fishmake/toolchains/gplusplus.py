import fishmake

class ToolChain(fishmake.ToolChain):
	def configure(self, app_config):
		print "Configure CXX"
		defaults = {
			"BUILD_DIR"  : "lib",
			"EXECUTABLE" : "false"
		}
		return self.doConfigure(file=".fishmake.erlc", extensions=["c", "cpp"], defaults=defaults, app_config=app_config)


	def compile(self):
		print "====> cxx"
		includes = " "
		for include in self.config.getDirs("INCLUDE_DIRS"):
			if include == "":
				continue
			includes += "-I " + include + " "

		print self.config.config

	def name(self):
		return "g++"