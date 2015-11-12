import fishmonger.toolchains as Self

Enabled  = {}
Provided = {
	"build"    : [
		"python",
#		"gplusplus",
		"erlc",
#		"jscc",
		"erl_app",
		"javac",
#		"scalac"
	],
	"clean"    : [
		"rpm"
	],
	"document" : [
		"edoc",
		"jsdoc",
#		"javadoc"
	],
	"external" : [
		"rebar"
	],
	"generate" : [
	],
	"install"  : [
		"python",
		"erlc",
		"erl_app",
		"erl_misc",
		"erl_config",
		"javac",
#		"scalac",
#		"scala_app"
#		"jar",
#		"java_app"
	],
	"internal" : [
	],
	
	"link"     : [
	],
	"package"  : [
#		"deb",
		"rpm"
	]
}

def init():
	Self.Provided
	"""
	init() -> no_return()

	Initializes and enables the provided toolchains.
	"""
	return reduce(lambda acc, key: acc | set(Provided[key]), Provided, set())

def enable(name):
	"""
	enable(string()::Name)

	Loads the module Name. Name bust be a module within the known PYTHONPATH.
	"""
	pass

def disable(name):
	"""
	disable(string()::Name)

	Disables the module that has been loaded at Name.
	"""
	pass

def get(name):
	"""
	get(string()::Name) -> module()|None

	Returns the module loaded at Name. If no module is loaded None is returned.
	"""
	pass

a = list(init())
a.sort()
print a