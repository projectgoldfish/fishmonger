import fishmonger
import fishmonger.path       as FishPath
import fishmonger.toolchains

import pybase.log as PyLog

import pyrcs      as RCS

class ToolChain(fishmonger.toolchains.ToolChain):
	def exts(self):
		return {}

	def packageFiles(self, app_dir, config):
		version = config["docker.version"]    if "docker.version" in config else RCS.getVersion(app_dir)
		repo    = config["docker.repo"] + "/" if "docker.repo"    in config else ""

		commands = []
		for src_file in src_files:
			tokens  = src_file.split("-")
			package = app_dir.basename()
			if len(tokens) > 1:
				package += "-{0}".format(tokens[1])

			commands.push("docker build -t {0}{1}:{2} -f {3} .".format(repo, package, version, src_file))
		return commands

	def package(self, app_dir, config, src_files):
		for f in src_files:
			f.copy(self.langlibFile(app_dir, f, "python", config["build_dir"]))
		return None

	def publishFiles(self, app_dir, config):
		

	def publish(self, app_dir, config, src_files):


