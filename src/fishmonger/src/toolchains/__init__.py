def internal():
	return [
		"python"
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
		"gplusplus",
		"erlc",
		"jscc",
		"erl_app",
		"javac"
	]

def link():
	return [
	]

def install():
	return [
		"erl_app",
		"jar",
		"java_app"
	]

def document():
	return [
		"edoc",
		"jsdoc",
		"javadoc"
	]
