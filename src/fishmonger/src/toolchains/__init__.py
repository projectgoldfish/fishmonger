## Python modules included

## PyBase modules included
import pybase.log  as PyLog
import pybase.find as PyFind

## Fishmonger modules included
import fishmonger.cache      as FishCache
import fishmonger.exceptions as FishExc

ShortNames = {}
Tools      = {}

ExternalTools = {} ## module() => 1
InternalTools = {} ## module() => 1

class API():
		NOT_IMPLEMENTED_OK, NOT_IMPLEMENTED_ERR = range(0,2)

class ToolType:
	INTERNAL, EXTERNAL = range(0, 2)

Provided = [
	## Erlang Tools
	("fishmonger.toolchains.edoc",    ToolType.INTERNAL),
	("fishmonger.toolchains.erlc",    ToolType.INTERNAL),
	("fishmonger.toolchains.erl_sys", ToolType.INTERNAL),
	("fishmonger.toolchains.rebar",   ToolType.EXTERNAL),

	## Python Tools
	("fishmonger.toolchains.python",  ToolType.INTERNAL)
]

def enable(name, tool_type=ToolType.INTERNAL, ignore_error_on_error=True):
	try:
		tool  = getattr(__import__(name, fromlist=["ToolChain"]), "ToolChain")()
		valid = False
		if hasattr(tool.check_sys, "__call__"):
			if FishCache.getToolVersion(name) != tool.version:
				valid = tool.check_sys()
				if isinstance(valid, bool):
					FishCache.setToolVersion(name, tool.version)
				else:
					raise FishExc.FishmongerToolchainException("Tools check_sys returns invalid result", tool=name, result=valid)
		elif tool.check_sys == API.NOT_IMPLEMENTED_OK:
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

		if   tool_type == ToolType.INTERNAL:
			InternalTools[name] = 1
		elif tool_type == ToolType.EXTERNAL:
			ExternalTools[name] = 1
		else:
			raise FishExc.FishmongerToolchainException("Invalid tool type given", tool_type=tool_type)
		return
	except AttributeError as e:
		#PyLog.error("Error loading module", module=name, error=e)
		if not ignore_error_on_error:
			raise e
	except ImportError as e:
		#PyLog.error("Error importing module", module=name)
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
	
	def srcExts():
		"""
		Source Extensions
		srcExts() -> [string()]

		Returns a list of the file extensions that this tool works with.

		This function MUST be implemented.
		"""
		return []

	def uses(config):
		"""
		Uses
		uses(string()) -> boolean

		Determines if the tool chain should act on the proposed configuration.
		"""
		return len(PyFind.findAllByExtensions(self.srcExts(), config.root)) == 0

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
	check_sys = API.NOT_IMPLEMENTED_OK

	"""
	Clean
	clean(config()) -> [command()] | ToolChain.NOT_IMPLEMENTED

	Cleans this build stage.
	"""
	clean = API.NOT_IMPLEMENTED_OK

	"""
	Generate
	generate(config()) -> [command()] | ToolChain.NOT_IMPLEMENTED

	Returns the list of commands() that must be run to generate code for the application.
	"""
	generate = API.NOT_IMPLEMENTED_OK

	"""
	Build
	build(config()) -> [command()] | ToolChain.NOT_IMPLEMENTED

	Returns the list of commands() that must be run to build the application.
	"""
	build = API.NOT_IMPLEMENTED_OK

	"""
	Link
	link(config()) -> [command()] | ToolChain.NOT_IMPLEMENTED

	Returns the list of commands() that must be run to link the application.
	"""
	link = API.NOT_IMPLEMENTED_OK

	"""
	Install
	install(config()) -> [command()] | ToolChain.NOT_IMPLEMENTED

	Returns the list of commands() that must be run to install the application.
	"""
	install = API.NOT_IMPLEMENTED_ERR

	"""
	Document
	document(config()) -> [command()] | ToolChain.NOT_IMPLEMENTED

	Returns the list of commands() that must be run to document the application.
	"""
	document = API.NOT_IMPLEMENTED_OK

	"""
	Package
	package(config()) -> [command()] | ToolChain.NOT_IMPLEMENTED

	Returns the list of commands() that must be run to package the application.
	"""
	package = API.NOT_IMPLEMENTED_OK

	"""
	Publish
	ppublish(config()) -> [command()] | ToolChain.NOT_IMPLEMENTED

	Returns the list of commands() that must be run to publish the application.
	"""
	publish = API.NOT_IMPLEMENTED_OK
