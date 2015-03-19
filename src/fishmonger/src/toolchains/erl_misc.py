import pybase.config
import pyerl       as PyErl
import pybase.util as PyUtil
import pybase.find as PyFind
import pyrcs       as PyRCS
import pybase.file as PyFile
import pybase.sh   as PySH
import pybase.set  as PySet
import pybase.log  as PyLog

import os.path
import shutil

import fishmonger
import fishmonger.utils.erl as FishErl

class ToolChain(fishmonger.ToolChain):	
	## gen_shell_script(dict()) -> None
	## Generates a shell script that will start the system
	## or attach to a runnign node.
	def genShellScript(self, app):
		app_name    = app.name()
		start_apps  = ""
		apps        = FishErl.getRequiredApps(app.name(), app.installDir())
		for tapp in apps:
			start_apps += "-eval \"application:start(" + tapp + ")\" "
		cookie_file = app.installVarDir(subdir="run", file=".cookie", version=False, absolute=True)
		file_name   = app.installBinDir(file=app_name)
		erl_dirs    = app.installLibDir(subdir="erlang/lib/", absolute=True)
		config_file = app.installEtcDir(file=app_name+".erl_config", absolute=True)

		file        = PyFile.file(file_name, "w")
		file.write("#! /bin/bash\n")
		file.write("export ERL_LIBS=${ERL_LIBS}:" + erl_dirs + "\n")
		file.write("erl  -name " + app_name +  "@`hostname -f` -setcookie \"`cat " + cookie_file + "`\" -config " + config_file +  " " + start_apps)
		file.close()

		PySH.cmd("chmod a+x " + file_name)

	def genShellConnectScript(self, app):
		app_name    = app.name()
		install_dir = app.installDir("")

		cookie_file = app.installVarDir(subdir="run", file=".cookie", version=False, absolute=True)
		file_name   = app.installBinDir(file=app_name + "-connect")
		erl_dirs    = app.installLibDir(subdir="erlang/lib/", absolute=True)

		file        = PyFile.file(file_name, "w")
		file.write("#! /bin/bash\n")
		file.write("export ERL_LIBS=${ERL_LIBS}:" + erl_dirs + "\n")
		file.write("erl -remsh " + app_name + "@`hostname -f` -name " + app_name + "-shell-$$ -setcookie \"`cat " + cookie_file + "`\"")
		file.close()
		PySH.cmd("chmod a+x " + file_name)

	def genShellEnvScript(self, app):
		app_name    = app.name()
		install_dir = app.installDir("")

		cookie_file = app.installVarDir(subdir="run", file=".cookie", version=False, absolute=True)
		file_name   = app.installBinDir(file=app_name + "-env")
		erl_dirs    = app.installLibDir(subdir="erlang/lib/", absolute=True)
		config_file = app.installEtcDir(file=app_name+".erl_config", absolute=True)

		file        = PyFile.file(file_name, "w")
		file.write("#! /bin/bash\n")
		file.write("export ERL_LIBS=${ERL_LIBS}:" + erl_dirs + "\n")
		file.write("erl -name " + app_name + "-shell-$$ -setcookie \"`cat " + cookie_file + "`\" -config " + config_file)
		file.close()
		PySH.cmd("chmod a+x " + file_name)

	## gen_cookie(dict()) -> None
	## Generates the cookie file
	def genCookie(self, app):
		PyLog.output("Baking cookie...")
		cookie_file = app.installVarDir(subdir="run", file=".cookie", version=False)
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

	def genDirs(self, app):
		log_dir = app.installVarDir(subdir="log", version=False, absolute=True)

		if not os.path.isdir(log_dir):
			PySH.mkdirs(log_dir)

	def installMisc(self, app):
		var_dir         = app.appDir("var")
		install_var_dir = app.installVarDir()
		if os.path.isdir(var_dir):
			PyLog.output("Copying content...")
			PySH.copy(var_dir, install_var_dir, force=True)

	def __init__(self):
		self.extensions = ["erl"]
		self.defaults   = {
			"BUILD_AFTER_TOOLS" : ["erl_app"],
			"TOOL_OPTIONS"      : {
				"ERL_MAIN"      : "",
				"EXECUTABLE"    : False
			}
		}

	def installApp(self, child, app):
		self.config = app
		self.installMisc(app)

		main_steps = [self.genShellScript, self.genShellEnvScript, self.genShellConnectScript, self.genCookie, self.genDirs]
		if app.name() == app["TOOL_OPTIONS"]["ERL_MAIN"] or ("EXECUTABLE" in app["APP_OPTIONS"] and app["APP_OPTIONS"]["EXECUTABLE"] == True):
			for step in main_steps:
				step(app)

