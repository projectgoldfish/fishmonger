## Python modules included

## PyBase modules included
import pybase.log  as PyLog
import pybase.find as PyFind

## Fishmonger modules included
import fishmonger.cache      as FishCache
import fishmonger.exceptions as FishExc

ShortNames = {}
Tools      = {}

ExclusiveTools = {} ## module() => 1
InclusiveTools = {} ## module() => 1

class API():
		NOT_IMPLEMENTED  = range(0,1)

class ToolType:
	INCLUSIVE, EXCLUSIVE = range(0, 2)

Provided = [
	## Docker Tools
	("fishmonger.toolchains.docker",  ToolType.INCLUSIVE),

	## Erlang Tools
	("fishmonger.toolchains.edoc",    ToolType.INCLUSIVE),
	("fishmonger.toolchains.erlc",    ToolType.INCLUSIVE),
	("fishmonger.toolchains.erl_sys", ToolType.INCLUSIVE),
	("fishmonger.toolchains.rebar",   ToolType.EXCLUSIVE),

	## Python Tools
	("fishmonger.toolchains.python",  ToolType.INCLUSIVE)
]

def enable(name, tool_type=ToolType.INCLUSIVE, ignore_error_on_error=True):
	try:
		tool  = getattr(__import__(name, fromlist=["ToolChain"]), "ToolChain")()
		valid = False
		if hasattr(tool.checkSys, "__call__"):
			key           = (name, tool.version())
			valid_version = FishCache.fetch(key, None)
			if valid_version != True:
				valid = tool.checkSys()
				if valid == True:
					FishCache.store(key, True)
				else:
					raise FishExc.FishmongerToolchainException("System does not meet tool requirements.", tool=name, reason=valid)
		elif tool.checkSys == API.NOT_IMPLEMENTED:
			valid = True
		else:
			raise FishExc.FishmongerToolchainException("Invalid value for tool.check_sys", check_sys=tool.check_sys)

		if valid:
			Tools[name] = tool
			_shortName(name)
			PyLog.debug("Loaded toolchain", name, log_level=2)
		else:
			if ignore_error_on_error:
				PyLog.warning("Tool does not meet system dependencies. Continuing without...", tool=name)
			raise FishExc.FishmongerToolchainException("Tool does not meet system dependencies.", tool=name)

		if   tool_type == ToolType.INCLUSIVE:
			InclusiveTools[name] = 1
		elif tool_type == ToolType.EXCLUSIVE:
			ExclusiveTools[name] = 1
		else:
			raise FishExc.FishmongerToolchainException("Invalid tool type given", tool_type=tool_type)
		return
	except AttributeError as e:
		PyLog.error("Error loading module", module=name, error=e)
		if not ignore_error_on_error:
			raise e
	except ImportError as e:
		PyLog.error("Error importing module", module=name)
		if not ignore_error_on_error:
			raise e
	PyLog.warning("Continuing without toolchain", name)


def _shortName(name):
	"""
	shortName(string()::Name) -> string()::Return

	Returns the last portions of a fully qualified module name. This is the
	name that is reported in the build steps.

	Example: fishmonger.toolchains.erlc -> erlc
	"""
	if name not in ShortNames:
		ShortNames[name] = name.split(".")[-1]
	return ShortNames[name]

def init():
	"""
	init() -> no_return()

	Initializes and enables the provided toolchains.
	"""
	map(lambda x: enable(*x), Provided)

class ToolChain():
	def exts(self):
		"""
		Source Extensions
		srcExts() -> [string()]

		Returns a list of the file extensions that this tool works with.

		This function MUST be implemented.
		"""
		raise FishExc.FishmongerToolchainException("Toolchain must define exts/1", toolchain=self)

	def _usedFiles(self, app_dir, exts):
		if len(exts) == 0:
			return []
		pattern  = reduce(lambda acc, ext: acc + "*." + ext, exts[1:], "*." + exts[0])
		return app_dir.find(pattern=pattern)

	def appFiles(self, app_dir):
		exts = reduce(lambda acc, exts: acc + exts, self.exts().values())
		return self._usedFiles(app_dir, exts)

	def stageFiles(self, app_dir, config, stage):
		return self._usedFiles(app_dir, self.exts().get(stage, []))	

	def configure(config):
		"""
		Configure
		configure(config()) -> config()

		Returns a configuration object updated with toolchain specific configuration.
		"""
		return config

	def dependencies(config):
		"""
		Dependencies
		dependencies(config()) -> [dependency()]

		Returns a list of dependency specs for this config(). This should return an empty list
		unless the tool supports dependencies, such as with rebar.
		"""
		return []

	def langlibFile(self, app_dir, app_file, language, stage_dir):
		return app_dir.langlib(language, stage_dir).join(app_file.relative(app_dir.join("src")))

	"""
	Version
	version - integer()

	Integer value that is to be increased whenever a tool is updated.
	This helps determine if we need to check system for dependencies.
	"""
	version = 1

	"""
	CheckSys
	check_sys() -> boolean() | ToolChain.NOT_IMPLEMENTED

	Validates system components exist
	"""
	checkSys = API.NOT_IMPLEMENTED

	"""
	Clean
	clean(config()) -> [command()] | ToolChain.NOT_IMPLEMENTED

	Cleans this build stage.
	"""
	clean = API.NOT_IMPLEMENTED

	"""
	Generate
	generate(config()) -> [command()] | ToolChain.NOT_IMPLEMENTED

	Returns the list of commands() that must be run to generate code for the application.
	"""
	generate      = API.NOT_IMPLEMENTED
	generateFiles = API.NOT_IMPLEMENTED

	"""
	Build
	build(config()) -> [command()] | ToolChain.NOT_IMPLEMENTED

	Returns the list of commands() that must be run to build the application.
	"""
	build      = API.NOT_IMPLEMENTED
	buildFiles = API.NOT_IMPLEMENTED

	"""
	Link
	link(config()) -> [command()] | ToolChain.NOT_IMPLEMENTED

	Returns the list of commands() that must be run to link the application.
	"""
	link      = API.NOT_IMPLEMENTED
	linkFiles = API.NOT_IMPLEMENTED

	"""
	Install
	install(config()) -> [command()] | ToolChain.NOT_IMPLEMENTED

	Returns the list of commands() that must be run to install the application.
	"""
	install      = API.NOT_IMPLEMENTED
	installFiles = API.NOT_IMPLEMENTED

	"""
	Document
	document(config()) -> [command()] | ToolChain.NOT_IMPLEMENTED

	Returns the list of commands() that must be run to document the application.
	"""
	document      = API.NOT_IMPLEMENTED
	documentFiles = API.NOT_IMPLEMENTED

	"""
	Package
	package(config()) -> [command()] | ToolChain.NOT_IMPLEMENTED

	Returns the list of commands() that must be run to package the application.
	"""
	package      = API.NOT_IMPLEMENTED
	packageFiles = API.NOT_IMPLEMENTED

	"""
	Publish
	ppublish(config()) -> [command()] | ToolChain.NOT_IMPLEMENTED

	Returns the list of commands() that must be run to publish the application.
	"""
	publish      = API.NOT_IMPLEMENTED
	publishFiles = API.NOT_IMPLEMENTED
