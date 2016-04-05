## Python3.4
import fishmonger
import fishmonger.path       as FishPath
import fishmonger.toolchains
## PIP
## Fishmonger
import fishmonger.rcs      as FishRCS

def model():
	def modelConfig():

	return modelConfig

class ToolChain(fishmonger.toolchains.ToolChain):
	def exts(self):
		return {}

	def packageFiles(self, app_dir, config):
		return {
			"as_needed" : [],
			"always"    : app_dir.find(pattern="Dockerfile*", files_only=True)
		}

	def package(self, app_dir, config, src_files):
		version = config["docker.version"]    if "docker.version" in config else FishRCS.getVersion(app_dir)
		repo    = config["docker.repo"] + "/" if "docker.repo"    in config else ""

		commands = []
		for src_file in src_files:
			tokens  = src_file.split("-")
			package = app_dir.basename()
			if len(tokens) > 1:
				package += "-{0}".format(tokens[1])

			commands.push("docker build -t {0}{1}:{2} -f {3} .".format(repo, package, version, src_file))
		return commands

	def publishFiles(self, app_dir, config):
		return {
			"as_needed" : [],
			"always"    : app_dir.find(pattern="Dockerfile*", files_only=True)
		}

	def publish(self, app_dir, config, src_files):
		version = config["docker.version"]    if "docker.version" in config else FishRCS.getVersion(app_dir)
		repo    = config["docker.repo"] + "/" if "docker.repo"    in config else ""

		commands = []
		for src_file in src_files:
			tokens  = src_file.split("-")
			package = app_dir.basename()
			if len(tokens) > 1:
				package += "-{0}".format(tokens[1])

			commands.push("docker push -t {0}{1}:{2}".format(repo, package, version))
		return commands

