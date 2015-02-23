def internal():
	return [
	]

def external():
	return [
#		"rebar"
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
#		"javac"
	]

def link():
	return [
	]

def install():
	return [
		"python",
		"erlc",
		"erl_app",
#		"jar",
#		"java_app"
	]

def document():
	return [
		"edoc",
		"jsdoc",
#		"javadoc"
	]
