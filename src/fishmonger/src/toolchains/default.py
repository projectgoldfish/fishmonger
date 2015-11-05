"""
Default

@author: Charles Zilm

Deafault fishmonger tool chain. Any tool chain that does not define an action will
use the behavior as it is defined here. Module should serve as a template/spec for all 
future modules.

Types as used by function documentation:

command()    - function(config()) -> boolean() | string() - When a string the value will be executed via shell. When a function it will be called with the config for the build stage.
config()     - BuildConfig()
boolean()    - True | False
dependency() - string() :: Name | (string() :: Name, string() :: Version)
"""

def src_exts():
	"""
	Source Extensions
	src_exts() -> [string()]

	Returns a list of the file extensions that this tool works with.

	This function MUST be implemented.
	"""
	pass

def uses(app):
	"""
	Uses
	uses(config()) -> boolean

	Determines if the tool chain should act on the proposed configuration.
	"""
	pass

def configure(app):
	"""
	Configure
	configure(config()) -> config()

	Returns a configuration object updated with toolchain specific configuration.
	"""
	pass

def dependencies(app):
	"""
	Dependencies
	dependencies(config()) -> [dependency()]

	Returns a list of dependency specs for this config(). This should return an empty list
	unless the tool supports dependencies, such as with rebar.
	"""
	pass

def clean(self, app):
	"""
	Clean
	clean(config()) -> [command()] | None

	Cleans this build stage.
	"""
	pass

## Build runs the commands that each app says to use.
def build(self, app):
	"""
	Build
	build(config()) -> [command()] | None

	Returns the list of commands() that must be run to build the application.
	"""
	pass

def install(self, app):
	"""
	Install
	install(config()) -> [command()] | None

	Returns the list of commands() that must be run to install the application.
	"""
	pass

def document(self, app):
	"""
	Document
	document(config()) -> [command()] | None

	Returns the list of commands() that must be run to document the application.
	"""
	pass

def generate(self, app):
	"""
	Generate
	generate(config()) -> [command()] | None

	Returns the list of commands() that must be run to generate code for the application.
	"""
	pass

def link(self, app):
	"""
	Link
	link(config()) -> [command()] | None

	Returns the list of commands() that must be run to link the application.
	"""
	pass

def package(self, app):
	"""
	Package
	package(config()) -> [command()] | None

	Returns the list of commands() that must be run to package the application.
	"""
	pass
