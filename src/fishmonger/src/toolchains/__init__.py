## Python modules included

## PyBase modules included
import pybase.log as PyLog

## Fishmonger modules included
import fishmonger.exceptions as FishExc

FullNames  = {}
ShortNames = {}
Enabled    = []

ExternalTools = {} ## module() => 1
InternalTools = {} ## module() => 1

class ToolType:
	INTERNAL, EXTERNAL = range(0, 2)

Provided = [
	## Erlang Tools
	("edoc",    ToolType.INTERNAL),
	("erlc",    ToolType.INTERNAL),
	("erl_sys", ToolType.INTERNAL),
	("rebar",   ToolType.EXTERNAL),

	## Python Tools
	("python",  ToolType.INTERNAL)
]

def init():
	"""
	init() -> no_return()

	Initializes and enables the provided toolchains.
	"""
	map(lambda x: enable(*x), Provided)

def enable(name, tool_type=ToolType.INTERNAL):
	"""
	enable(string()::Name)

	Loads the module Name. Name bust be a module within the known PYTHONPATH. An 
	error is thrown if the module short name has been used.
	"""
	if name in FullNames:
		raise FishExc.FishmongerToolchainException("Toolchain with short name has already been loaded", short_name=sname, full_name=name, existing=FullNames[sname])
	
	sname          = shortName(name)
	Enabled[sname] = importlib.import_module(name)

def shortName(name):
	"""
	shortName(string()::Name) -> string()::Return

	Returns the last portions of a fully qualified module name. This is the
	name that is reported in the build steps.

	Example: fishmonger.toolchains.erlc -> erlc
	"""
	if name not in ShortNames:
		ShortNames[name] = name.split(".")[-1]
	return ShortNames[name]

def fullName(name):
	"""
	fullName(string()::Name) -> string()::Return

	Returns the full name associated with the given short name.
	An error is thrown if no full name exists.

	Example: erlc -> fishmonger.toolchains.erlc
	"""
	if name not in FullNames:
		raise FishExc.FishmongerToolchainException("No full name has been given for short name", short_name=name)
	return FullNames[name]

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
		return 

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

	def clean(self, app):
		"""
		Clean
		clean(config()) -> [command()] | None

		Cleans this build stage.
		"""
		return None

	def generate(self, app):
		"""
		Generate
		generate(config()) -> [command()] | None

		Returns the list of commands() that must be run to generate code for the application.
		"""
		return None

	def build(self, app):
		"""
		Build
		build(config()) -> [command()] | None

		Returns the list of commands() that must be run to build the application.
		"""
		return None

	def link(self, app):
		"""
		Link
		link(config()) -> [command()] | None

		Returns the list of commands() that must be run to link the application.
		"""
		return None

	def install(self, app):
		"""
		Install
		install(config()) -> [command()] | None

		Returns the list of commands() that must be run to install the application.
		"""
		return None

	def document(self, app):
		"""
		Document
		document(config()) -> [command()] | None

		Returns the list of commands() that must be run to document the application.
		"""
		return None

	def package(self, app):
		"""
		Package
		package(config()) -> [command()] | None

		Returns the list of commands() that must be run to package the application.
		"""
		return None

	def publish(self, app):
		"""
		Publish
		ppublish(config()) -> [command()] | None

		Returns the list of commands() that must be run to publish the application.
		"""
		return None
