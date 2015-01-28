import pybase.config
import pyerl       as PyErl
import pybase.util as PyUtil
import pybase.find as PyFind
import pyrcs       as PyRCS
import pybase.file as PyFile
import pybase.sh   as PySH
import os.path
import shutil

import fishmonger

class ErlApp(object):
	def __init__(self, file, app):
		self.app   = app
		self.doc = PyErl.parse_file(file)
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

		for mod in PyFind.findFilesByExts(["erl"], self.app.appDir()):
			(mod, x) = os.path.splitext(mod)
			modules_tuple[1].appendChild(PyErl.PyErlString(mod))
		arg_list.appendChild(modules_tuple)

	def addVersion(self):
		arg_list = self.doc.getElementsByTagName("list")[0]
		
		## If a vsn has already been specified leave it.
		for term in arg_list:
			if hasattr(term, '__iter__') and term[0].getValue == "vsn":
				return

		version_tuple = PyErl.PyErlTuple()
		version_tuple.appendChild(PyErl.PyErlAtom("vsn"))

		version = PyErl.PyErlString(PyRCS.getVersion())	

		version_tuple.appendChild(version)
		arg_list.appendChild(version_tuple)
	
	def addId(self):
		arg_list = self.doc.getElementsByTagName("list")[0]
		
		## If a vsn has already been specified leave it.
		for term in arg_list:
			if hasattr(term, '__iter__') and term[0].getValue == "id":
				return

		id_tuple = PyErl.PyErlTuple()
		id_tuple.appendChild(PyErl.PyErlAtom("id"))

		id = PyErl.PyErlString(PyRCS.getId())
		id_tuple.appendChild(id)
		arg_list.appendChild(id_tuple)

class ToolChain(fishmonger.ToolChain):	
	## Looks in each app dir for a $APP.app.fish file
	## uses it to generate a .app
	def genApp(self, app):
		app_src  = app.srcDir(app.name + ".app.erlc")
		app_file = app.buildDir(app.name + ".app")
		if os.path.isfile(app_src):
			doc  = ErlApp(app_src, app)
			doc.write(app_file)
		else:
			app_src = app.srcDir(app.name + ".app")
			if os.path.isfile(app_src):
				shutil.copyfile(app_src, app_file)


	## Look at the applications entry of the app.
	## If we have app.app in our intall directory then
	## get it's apps as well.
	## If we don't assume it's a native app.
	def getApps(self, app):
		apps = []
		app_file = PyFind.find(app + ".app", self.config["INSTALL_PREFIX"])
		if not app_file:
			app_file = PyFind.find(app + ".app", "/usr/lib/erlang") ## Search in a nix install
			if not app_file:
				app_file = PyFind.find(app + ".app", "/usr/local/lib/erlang") ## Search in an OSX install
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
			tapps = self.getApps(dapp.to_string())
			for tapp in tapps:
				if not tapp in apps:
					 apps.append(tapp)
		apps.append(app)
		return apps

	## gen_shell_script(dict()) -> None
	## Generates a shell script that will start the system
	## or attach to a runnign node.
	def genShellScript(self, app):
		app_name    = app.name
		start_apps  = ""
		apps        = self.getApps(app.name)
		for tapp in apps:
			start_apps += "-eval \"application:start(" + tapp + ")\" "
		cookie_file = os.path.join(app.installAppDir("var/run", version=False), ".cookie")
		file_name   = os.path.join(app.installDir("bin"),     app_name)
		erl_dirs    = app.installDir("lib/erlang/lib/")
		config_file = os.path.join(app.installDir("etc"), app_name + ".config")

		file        = PyFile.file(file_name, "w")
		file.write("#! /bin/bash\n")
		file.write("export ERL_LIBS=${ERL_LIBS}:" + erl_dirs + "\n")
		file.write("erl  -name " + app_name +  "@`hostname -f` -setcookie \"`cat " + cookie_file + "`\" -config " + config_file +  " " + start_apps)
		file.close()
		PySH.cmd("chmod a+x " + file_name)

	def genShellConnectScript(self, app):
		app_name    = app.name
		install_dir = app.installDir("")

		cookie_file = os.path.join(app.installAppDir("var/run", version=False), ".cookie")
		file_name   = os.path.join(app.installDir("bin"),     app_name + "-connect")
		erl_dirs    = app.installDir("lib/erlang/lib/")

		file        = PyFile.file(file_name, "w")
		file.write("#! /bin/bash\n")
		file.write("export ERL_LIBS=${ERL_LIBS}:" + erl_dirs + "\n")
		file.write("erl -remsh " + app_name + "@`hostname -f` -name " + app_name + "-shell-$$ -setcookie \"`cat " + cookie_file + "`\"")
		file.close()
		PySH.cmd("chmod a+x " + file_name)

	def genShellEnvScript(self, app):
		app_name    = app.name
		install_dir = app.installDir("")

		cookie_file = os.path.join(app.installAppDir("var/run", version=False), ".cookie")
		file_name   = os.path.join(app.installDir("bin"),     app_name + "-env")
		erl_dirs    = app.installDir("lib/erlang/lib/")
		config_file = os.path.join(app.installDir("etc"), app_name + ".config")

		file        = PyFile.file(file_name, "w")
		file.write("#! /bin/bash\n")
		file.write("export ERL_LIBS=${ERL_LIBS}:" + erl_dirs + "\n")
		file.write("erl -name " + app_name + "-shell-$$ -setcookie \"`cat " + cookie_file + "`\" -config " + config_file)
		file.close()
		PySH.cmd("chmod a+x " + file_name)

	## gen_cookie(dict()) -> None
	## Generates the cookie file
	def genCookie(self, app):
		print "======> Baking cookie..."
		cookie_dir  = app.installAppDir("var/run", version=False)
		if not os.path.isdir(cookie_dir):
			os.makedirs(cookie_dir)
		cookie_file = os.path.join(cookie_dir, ".cookie")
		try:
			os.remove(cookie_file)
		except OSError, e:
			pass

		cookie = "snickerdoodle"
		if self.config["ERL_COOKIE"] != None:
			cookie = self.config["ERL_COOKIE"]
		else:
			cookie = "cookie_flavor-" + PyRCS.getVersion() + "-" + PyRCS.getId()

		file = PyFile.file(cookie_file, "w")
		file.write(cookie)
		file.close()
		PySH.cmd("chmod a-x "  + cookie_file)
		PySH.cmd("chmod a-w "  + cookie_file)
		PySH.cmd("chmod og-r " + cookie_file)

	def genConfigFile(self, app):
		doc         = PyErl.PyErlDocument()
		expressions = PyErl.PyErlList()
		config_file = app.installDir("etc/" + app.name + ".config.default")
		apps        = self.getApps(app.name)

		print "======> Generating config..."

		for app in self.apps:
			if app.name not in apps:
				continue
			app_config = app.appDir("etc/" + app.name + ".config")
			if os.path.isfile(app_config):
				terms = PyErl.parse_file(app_config)
				expressions.appendChild(terms)

		doc.appendChild(expressions)
		PyErl.write_file(config_file, doc)

	def installMisc(self, app):
		var_dir         = app.appDir("var")
		install_var_dir = app.installDir("var")
		print "======> Copying content..."
		if os.path.isdir(var_dir):
			PySH.copy(var_dir, install_var_dir, force=True)

	def __init__(self):
		self.extensions = ["erl"]
		self.defaults   = {
			"BUILD_DIR"  : "ebin",
			"EXECUTABLE" : "false"
		}

	def buildApp(self, app):
		return [self.genApp]

	def installApp(self, app):
		self.config = app
		self.installMisc(app)

		main_steps = [self.genShellScript, self.genShellEnvScript, self.genShellConnectScript, self.genConfigFile, self.genCookie]
		if app.name == app["ERL_MAIN"] or app["EXECUTABLE"] == True:
			for step in main_steps:
				step(app)

