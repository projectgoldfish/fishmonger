## Python modules included
import importlib

## PyBase modules included
import pybase.log as PyLog

## Fishmonger modules included
import fishmonger.exceptions as FishExc

FullNames  = {}
ShortNames = {}
Enabled    = {}

All        = {}
Nix        = {
	"build"    : [
#		"fishmonger.toolchains.python",
#		"fishmonger.toolchains.gplusplus",
#		"fishmonger.toolchains.erlc",
#		"fishmonger.toolchains.jscc",
#		"fishmonger.toolchains.erl_app",
#		"fishmonger.toolchains.javac",
#		"fishmonger.toolchains.scalac"
	],
	"clean"    : [
#		"fishmonger.toolchains.rpm"
	],
	"document" : [
#		"fishmonger.toolchains.edoc",
#		"fishmonger.toolchains.jsdoc",
#		"fishmonger.toolchains.javadoc"
	],
	"external" : [
#		"fishmonger.toolchains.rebar"
	],
	"generate" : [
	],
	"install"  : [
#		"fishmonger.toolchains.python",
#		"fishmonger.toolchains.erlc",
#		"fishmonger.toolchains.erl_app",
#		"fishmonger.toolchains.erl_misc",
#		"fishmonger.toolchains.erl_config",
#		"fishmonger.toolchains.javac",
#		"fishmonger.toolchains.scalac",
#		"fishmonger.toolchains.scala_app"
#		"fishmonger.toolchains.jar",
#		"fishmonger.toolchains.java_app"
	],
	"internal" : [
	],
	
	"link"     : [
	],
	"package"  : [
#		"fishmonger.toolchains.deb",
#		"fishmonger.toolchains.rpm"
	]
}
Osx        = {}
Win        = {}

Provided   = {
	"all" : All,
	"nix" : Nix,
	"osx" : Osx,
	"win" : Win
}

def init():
	"""
	init() -> no_return()

	Initializes and enables the provided toolchains.
	"""

	os     = getOs()
	foros  = reduce(lambda acc, key: acc | set(Provided[os][key]),    Provided[os],    set())
	forall = reduce(lambda acc, key: acc | set(Provided["all"][key]), Provided["all"], set())
	map(enable, foros | forall)

def replace(name):
	"""
	replace(string()::Name)

	Loads the module Name. Name bust be a module within the known PYTHONPATH.
	If the module short name has previously been used this module wll replace it.
	"""
	sname          = shortName(name)
	Enabled[sname] = importlib.import_module(name)

def enable(name):
	"""
	enable(string()::Name)

	Loads the module Name. Name bust be a module within the known PYTHONPATH. An 
	error is thrown if the module short name has been used.
	"""
	sname          = shortName(name)
	if sname in FullNames:
		raise FishExc.FishmongerToolchainException("Toolchain with short name has already been loaded", short_name=sname, full_name=name, existing=FullNames[sname])
	Enabled[sname] = importlib.import_module(name)

def disable(name):
	"""
	disable(string()::Name)

	Disables the module that has been loaded at Name.
	"""
	sname = shortName(name)
	del Enabled[sname]

def get(name):
	"""
	get(string()::Name) -> module()|None

	Returns the module loaded at Name. If no module is loaded None is returned.
	"""
	return Enabled.get(shortName(name), None)

def getOs():
	"""
	getOs() -> "nix"|"osx"|"win"

	Returns a 3 character string signifying the type of operating system is in use.
	This is used when determining which version of toolchains to use.
	"""
	return "nix"

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

init()
