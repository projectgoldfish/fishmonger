def internal():
	return [
	]

def clean():
	return [
		"rpm"
	]

def external():
	return [
		"rebar"
	]

def generate():
	return [
	]

def build():
	return [
		"python",
#		"gplusplus",
		"erlc",
#		"jscc",
		"erl_app",
		"javac",
		#"scalac"
	]

def link():
	return [
	]

def install():
	return [
		"python",
		"erlc",
		"erl_app",
		"erl_misc",
		"erl_config",
		"javac",
		#"scalac",
		#"scala_app"
#		"jar",
#		"java_app"
	]

def document():
	return [
		"edoc",
		"jsdoc",
#		"javadoc"
	]

def package():
	return [
#		"deb",
		"rpm"
	]