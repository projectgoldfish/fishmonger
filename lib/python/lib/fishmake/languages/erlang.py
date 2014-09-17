from   pybase.config import Config as PyConfig
import pybase.config
import pyerl       as PyErl
import pybase.util as PyUtil
import pybase.dir  as PyDir
import os.path
import shutil

## Directories found in a built erlang src dir.
dirs  = ["ebin", "priv"]

def getFileTypes():
	return ["erl"]

class ErlApp():
	def __init__(self, file):
		dir  = os.path.dirname(file)
		base = os.path.basename(file)
		app  = base.split(":")[0]

		self.app_name = app
		self.dir      = dir
		self.doc      = PyErl.parse_file(file)

		self.addModules()
		self.addVersion()
		self.addId()

	def write(self, file):
		PyErl.write_file(file, self.doc)

	def addModules(self):
		arg_list = self.doc.getElementsByTagName("list")[0]
		for term in arg_list:
			if hasattr(term, '__iter__') and term[0].getValue == "modules":
				return

		modules_tuple = PyErl.term("{modules, []}.")

		for mod in PyDir.findFilesByExts(["erl"], self.dir):
			print mod


		modules_tuple[1].appendChild(PyErl.PyErlString(PyConfig["APP_VERSION"]))
		arg_list.appendChild(modules_tuple)

	def addVersion(self):
		arg_list = self.doc.getElementsByTagName("list")[0]
		
		## If a vsn has already been specified leave it.
		for term in arg_list:
			if hasattr(term, '__iter__') and term[0].getValue == "vsn":
				return

		version_tuple = PyErl.PyErlTuple()
		version_tuple.appendChild(PyErl.PyErlAtom("vsn"))
		version_tuple.appendChild(PyErl.PyErlString(PyConfig["APP_VERSION"]))
		arg_list.appendChild(version_tuple)
	
	def addId(self):
		arg_list = self.doc.getElementsByTagName("list")[0]
		
		## If a vsn has already been specified leave it.
		for term in arg_list:
			if hasattr(term, '__iter__') and term[0].getValue == "id":
				return

		id_tuple = PyErl.PyErlTuple()
		id_tuple.appendChild(PyErl.PyErlAtom("id"))
		id_tuple.appendChild(PyErl.PyErlString(PyConfig["APP_ID"]))
		arg_list.appendChild(id_tuple)
		
## Looks in each app dir for a $APP.app.fish file
## uses it to generate a .app
def genApp(path):
	app      = os.path.basename(path)
	app_src  = os.path.join(path, "src/"  + app + ".app.fish")
	app_file = os.path.join(path, "ebin/" + app + ".app")
	
	if os.path.isfile(app_src):
		doc  = ErlApp(app_src)
		doc.write(app_file)

## gen_shell_script(dict()) -> None
## Generates a shell script that will start the system
## or attach to a runnign node.
def genShellScript(install_dir, app_name, app_main):
	start_apps  = ""
	apps        = getApps(app_main)

	for app in apps:
		start_apps += "-eval \"application:start(" + app + ")\" "

	cookie_file = os.path.join(install_dir, "var/run/.cookie")
	file_name   = os.path.join(install_dir, "bin/" + app_name)
	erl_dirs    = os.path.join(install_dir, "lib/erlang/lib/*/ebin")
	erl_deps    = os.path.join(install_dir, "lib/erlang/lib/*/deps/*/ebin")
	config_file = os.path.join(install_dir, "etc/" + app_name + ".config")
	file        = open(file_name, "w")
	file.write("#! /bin/bash\n")
	file.write("erl -pa " + erl_dirs + " -pa " + erl_deps + " -name " + app_name +  "@`hostname -f` -setcookie \"`cat " + cookie_file + "`\" -config " + config_file +  " " + start_apps)
	file.close()
	PyUtil.shell("chmod a+x " + file_name)


def genShellConnectScript(install_dir, app_name):
	cookie_file = os.path.join(install_dir, "var/run/.cookie")
	file_name   = os.path.join(install_dir, "bin/" + app_name + "-connect")
	erl_dirs    = os.path.join(install_dir, "lib/erlang/lib/*/ebin")
	erl_deps    = os.path.join(install_dir, "lib/erlang/lib/*/debs/*/ebin")

	file        = open(file_name, "w")
	file.write("#! /bin/bash\n")
	file.write("erl -remsh " + app_name + "@`hostname -f` -pa " + erl_dirs + " -pa " + erl_deps + " -name " + app_name + "-shell-$$ -setcookie \"`cat " + cookie_file + "`\"")
	file.close()
	PyUtil.shell("chmod a+x " + file_name)

def genShellEnvScript(install_dir, app_name):
	cookie_file = os.path.join(install_dir, "var/run/.cookie")
	file_name   = os.path.join(install_dir, "bin/" + app_name + "-env")
	erl_dirs    = os.path.join(install_dir, "lib/erlang/lib/*/ebin")
	erl_deps    = os.path.join(install_dir, "lib/erlang/lib/*/debs/*/ebin")
	config_file = os.path.join(install_dir, "etc/" + app_name + ".config")

	file        = open(file_name, "w")
	file.write("#! /bin/bash\n")
	file.write("erl -pa " + erl_dirs + " -pa " + erl_deps + " -name " + app_name + "-shell-$$ -setcookie \"`cat " + cookie_file + "`\" -config " + config_file)
	file.close()
	PyUtil.shell("chmod a+x " + file_name)

## gen_cookie(dict()) -> None
## Generates the cookie file
def genCookie():
	file_name = PyDir.makeDirAbsolute(os.path.join(PyConfig["INSTALL_DIR"], "var/run/.cookie"))
	
	try:
		os.remove(file_name)
	except OSError, e:
		pass

	file = open(file_name, "w")
	file.write(PyConfig["APP_COOKIE"])
	file.close()
	PyUtil.shell("chmod a-x "  + file_name)
	PyUtil.shell("chmod a-w "  + file_name)
	PyUtil.shell("chmod og-r " + file_name)

def genConfigFile():
	doc         = PyErl.PyErlDocument()
	expressions = PyErl.PyErlList()
	config_file = os.path.join(PyConfig["INSTALL_DIR"], "etc/" + PyConfig["APP_MAIN"] + ".config.default")
	for app_dir in PyConfig["APP_DIRS"]:
		app        = os.path.basename(app_dir)
		app_config = os.path.join(app_dir, "etc/" + app + ".config")
		if os.path.isfile(app_config):
			terms = PyErl.parse_file(app_config)
			expressions.appendChild(terms)

	doc.appendChild(expressions)
	PyErl.write_file(config_file, doc)

## Look at the applications entry of the app.
## If we have app.app in our intall directory then
## get it's apps as well.
## If we don't assume it's a native app.
def getApps(app):
	apps = []
	
	app_file = PyDir.find(app + ".app", PyConfig["INSTALL_DIR"])
	if not app_file:
		app_file = PyDir.find(app + ".app", "/usr/lib/erlang") ## Search in a nix install
		if not app_file:
			app_file = PyDir.find(app + ".app", "/usr/local/lib/erlang") ## Search in an OSX install
			if not app_file:
				return [app]

	(doc, ) = PyErl.parse_file(app_file),

	tuples = doc.getElementsByTagName("tuple")
	tuple = None
	for ttuple in tuples:
		if ttuple[0].to_string() == "applications":
			tuple = ttuple
			break

	if tuple == None:
		return [app]

	for dapp in tuple[1]:
		tapps = getApps(dapp.to_string())
		for tapp in tapps:
			if not tapp in apps:
				 apps.append(tapp)
	apps.append(app)
	return apps

def compile(path):
	print "====> Erlang"
	config = pybase.config.merge(PyConfig, pybase.config.parse(".fishmake.erl"))
	
	includes = " "
	for include in config["INCLUDE_DIRS"]:
		if include == "":
			continue
		includes += "-I " + include + " "

	output_dir = os.path.join(path, "ebin")
	if not os.path.isdir(output_dir):
		os.mkdir(output_dir)
		
	print "======> Generating application config"
	genApp(path)
	print "======> Application config generated."
	print "======> Compiling *.erl to *.beam"
	cmd = "erlc " + includes + "-o " + output_dir + " " + os.path.join(path, "src/*.erl")
	print "======> Beams generated"
	return PyUtil.shell(cmd)

def systemInstall():
	print "====> Generating statup scripts..."
	genShellScript(       PyConfig["INSTALL_DIR"], PyConfig["APP_NAME"], PyConfig["APP_MAIN"])
	genShellConnectScript(PyConfig["INSTALL_DIR"], PyConfig["APP_NAME"])
	genShellEnvScript(    PyConfig["INSTALL_DIR"], PyConfig["APP_NAME"])
	print "====> Statup scripts generated..."
	print "====> Baking cookie"
	genCookie()
	print "====> Cookie baked"

def appInstall(path):
	basename        = os.path.basename(path)
	install_erl_dir = PyDir.makeDirAbsolute(os.path.join(PyConfig["INSTALL_DIR"], "lib/erlang/lib/" + basename + "-" + PyConfig["APP_VERSION"]))
		
	print "====> Copying Erlang binaries..."
	## Clear conflicting versions
	if os.path.exists(install_erl_dir):
		PyUtil.shell("rm -rf " + install_erl_dir)
	
	## Create the erlang lib directory
	if not os.path.exists(install_erl_dir):
		os.makedirs(install_erl_dir)

	for erl_dir in dirs:
		src_dir = os.path.join(path, erl_dir)
		erl_dir = os.path.join(install_erl_dir, erl_dir)
		if os.path.exists(src_dir):
			shutil.copytree(src_dir, erl_dir)
	print "====> Erlang binaries copied!"

	return 0

def doc(path):
	pass

