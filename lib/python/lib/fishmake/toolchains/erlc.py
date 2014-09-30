import pybase.config
import pyerl       as PyErl
import pybase.util as PyUtil
import pybase.dir  as PyDir
import os.path
import shutil

import fishmake

class ToolChain(fishmake.ToolChain):
	class ErlApp():
		def __init__(self, file, config):
			dir  = os.path.dirname(file)
			base = os.path.basename(file)
			app  = base.split(":")[0]

			self.config   = config
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
			version_tuple.appendChild(PyErl.PyErlString(self.config["APP_VERSION"]))
			arg_list.appendChild(version_tuple)
		
		def addId(self):
			arg_list = self.doc.getElementsByTagName("list")[0]
			
			## If a vsn has already been specified leave it.
			for term in arg_list:
				if hasattr(term, '__iter__') and term[0].getValue == "id":
					return

			id_tuple = PyErl.PyErlTuple()
			id_tuple.appendChild(PyErl.PyErlAtom("id"))
			id_tuple.appendChild(PyErl.PyErlString(self.config["APP_ID"]))
			arg_list.appendChild(id_tuple)
			
	## Looks in each app dir for a $APP.app.fish file
	## uses it to generate a .app
	def genApp(self, path):
		app      = os.path.basename(path)
		app_src  = os.path.join(path, "src/"  + app + ".app.fish")
		app_file = os.path.join(path, "ebin/" + app + ".app")
		
		if os.path.isfile(app_src):
			doc  = self.ErlApp(app_src, self.config)
			doc.write(app_file)

	## Look at the applications entry of the app.
	## If we have app.app in our intall directory then
	## get it's apps as well.
	## If we don't assume it's a native app.
	def getApps(self, app):
		apps = []
		
		app_file = PyDir.find(app + ".app", self.config["INSTALL_DIR"])
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
			tapps = self.getApps(dapp.to_string())
			for tapp in tapps:
				if not tapp in apps:
					 apps.append(tapp)
		apps.append(app)
		return apps

	## gen_shell_script(dict()) -> None
	## Generates a shell script that will start the system
	## or attach to a runnign node.
	def genShellScript(self):
		app_name    = self.config["APP_NAME"]
		app_main    = self.config["APP_MAIN"]
		install_dir = self.config["INSTALL_DIR"]

		start_apps  = ""
		apps        = self.getApps(app_main)

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

	def genShellConnectScript(self):
		app_name    = self.config["APP_NAME"]
		install_dir = self.config["INSTALL_DIR"]

		cookie_file = os.path.join(install_dir, "var/run/.cookie")
		file_name   = os.path.join(install_dir, "bin/" + app_name + "-connect")
		erl_dirs    = os.path.join(install_dir, "lib/erlang/lib/*/ebin")
		erl_deps    = os.path.join(install_dir, "lib/erlang/lib/*/debs/*/ebin")

		file        = open(file_name, "w")
		file.write("#! /bin/bash\n")
		file.write("erl -remsh " + app_name + "@`hostname -f` -pa " + erl_dirs + " -pa " + erl_deps + " -name " + app_name + "-shell-$$ -setcookie \"`cat " + cookie_file + "`\"")
		file.close()
		PyUtil.shell("chmod a+x " + file_name)

	def genShellEnvScript(self):
		app_name    = self.config["APP_NAME"]
		install_dir = self.config["INSTALL_DIR"]

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
	def genCookie(self):
		file_name = PyDir.makeDirAbsolute(os.path.join(self.config["INSTALL_DIR"], "var/run/.cookie"))
		try:
			os.remove(file_name)
		except OSError, e:
			pass

		file = open(file_name, "w")
		file.write(self.config["APP_COOKIE"])
		file.close()
		PyUtil.shell("chmod a-x "  + file_name)
		PyUtil.shell("chmod a-w "  + file_name)
		PyUtil.shell("chmod og-r " + file_name)

	def genConfigFile(self):
		doc         = PyErl.PyErlDocument()
		expressions = PyErl.PyErlList()
		config_file = os.path.join(self.config["INSTALL_DIR"], "etc/" + self.config["APP_MAIN"] + ".config.default")
		for app_dir in self.config["APP_DIRS"]:
			app        = os.path.basename(app_dir)
			app_config = os.path.join(app_dir, "etc/" + app + ".config")
			if os.path.isfile(app_config):
				terms = PyErl.parse_file(app_config)
				expressions.appendChild(terms)

		doc.appendChild(expressions)
		PyErl.write_file(config_file, doc)

	def mkDirs(self):
		install_dir = os.path.join(self.config["INSTALL_DIR"], "lib/erlang/lib")
		if not os.path.exists(install_dir):
			os.makedirs(install_dir)

	def installSystem(self):
		print "==> Preparing system..."
		steps = [self.genCookie, self.genConfigFile, self.mkDirs]
		for step in steps:
			step()
		print "==> System prepared!"

	def installApps(self):
		main_steps = [self.genShellScript, self.genShellEnvScript, self.genShellConnectScript]
		for app, app_dir, app_config in self.config["APP_CONFIG"]:
			app_dir = os.path.join(self.config["SRC_DIR"], app_dir)
			print "==> Installing app", app
			
			if app == self.config["APP_MAIN"] or app_config["EXECUTABLE"] == True:
				for step in main_steps:
					step()

			## copy binaries
			install_erl_dir = os.path.join(self.config["INSTALL_DIR"], "lib/erlang/lib/" + app + "-" + self.config["APP_VERSION"])
			if os.path.exists(install_erl_dir):
				PyUtil.shell("rm -rf " + install_erl_dir)
			for dir in ["priv", "ebin"]:
				install_target = os.path.join(install_erl_dir, dir)
				os.makedirs(install_target)
				if os.path.isdir(os.path.join(app_dir, dir)):
					PyDir.copytree(os.path.join(app_dir, dir), install_target)

			self.installMisc(app)
			print "==>", os.path.basename(app), "installed!"

	def installMisc(self, path):
		basename = os.path.basename(path)
		var_dir  = PyDir.makeDirAbsolute(os.path.join(path, "var"))
		doc_dir  = PyDir.makeDirAbsolute(os.path.join(path, "doc"))
		
		print "====> Copying variable content..."
		if os.path.exists(var_dir):
			PyDir.copytree(var_dir, install_var_dir)
		print "====> Variable content copied!"

	def installShellScripts(self):
		main_steps = [self.genShellScript, self.genShellEnvScript, self.genShellConnectScript]
		for app, app_dir, app_config in self.config["APP_CONFIG"]:
			app_dir = os.path.join(self.config["SRC_DIR"], app_dir)
				
			if app == self.config["APP_MAIN"] or app_config["EXECUTABLE"] == True:
				print "====> Installing shell scripts"
				for step in main_steps:
					step()

	def installDependencies(self):
		pass

	## What follows is the fishmake language api
	## All of the following variables and functions must be made available.
	def __init__(self):
		pass
	
	## Generate language specific configuration
	## Return True if we are used, false if not
	def configure(self, config):
		defaults = {
			"BUILD_DIR" : "ebin"
		}
		return self.do_configure(".fishmake.erlc", ["erl"], config, defaults)

	def compile(self):
		print "=> Erlang"
		includes = " "
		for include in self.config["INCLUDE_DIRS"]:
			if include == "":
				continue
			includes += "-I " + include + " "

		res = 0
		for app, app_dir, app_config in self.config["APP_CONFIG"]:
			print "==> Beginning", app
			app_dir    = os.path.join("src", app_dir)
			output_dir = os.path.join(app_dir, "ebin")
			if not os.path.isdir(output_dir):
				os.mkdir(output_dir)
			print "==> Generating application config"
			self.genApp(app_dir)
			print "==> Application config generated."
			print "==> Compiling *.erl to *.beam"
			cmd = "erlc " + includes + "-o " + app_config["BUILD_DIR"] + " " + os.path.join(app_dir, "src/*.erl")
			res = PyUtil.shell(cmd)
			if res != 0:
				print "==> Error compiling"
				return res
			print "==> Beams generated"
		return res

	def install(self):
		install_dir = os.path.join(self.config["INSTALL_DIR"], "lib/erlang/lib")
		if not os.path.exists(install_dir):
			os.makedirs(install_dir)
		self.installSystem()
		self.installApps()
		self.installShellScripts()
		self.installDependencies()
		return 0

	def doc(self):
		doc_dir = os.path.join(self.config["INSTALL_DIR"], "doc/erlang")
		print "==> Installing documentation..."
		for app, app_dir, app_config in self.config["APP_CONFIG"]:
			target_dir = os.path.join(doc_dir, app + "-" + self.config["APP_VERSION"])
			PyUtil.shell("erl -noshell -run edoc_run application '" + app + "' '\"" + app_dir + "\"' '[{dir, \"" + target_dir + "\"}]'")
		print "==> Documentation installed!"

