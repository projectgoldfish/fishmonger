from pybase.config import Config as PyConfig

import os
import os.path
import fishmake

import pybase.dir  as PyDir
import pybase.util as PyUtil

import pyerl       as PyErl

import shutil

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

## gen_shell_script(dict()) -> None
## Generates a shell script that will start the system
## or attach to a runnign node.
def genShellScript():
	app_name    = PyConfig["APP_NAME"]
	app_main    = PyConfig["APP_MAIN"]
	install_dir = PyConfig["INSTALL_DIR"]

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

def genShellConnectScript():
	app_name    = PyConfig["APP_NAME"]
	install_dir = PyConfig["INSTALL_DIR"]

	cookie_file = os.path.join(install_dir, "var/run/.cookie")
	file_name   = os.path.join(install_dir, "bin/" + app_name + "-connect")
	erl_dirs    = os.path.join(install_dir, "lib/erlang/lib/*/ebin")
	erl_deps    = os.path.join(install_dir, "lib/erlang/lib/*/debs/*/ebin")

	file        = open(file_name, "w")
	file.write("#! /bin/bash\n")
	file.write("erl -remsh " + app_name + "@`hostname -f` -pa " + erl_dirs + " -pa " + erl_deps + " -name " + app_name + "-shell-$$ -setcookie \"`cat " + cookie_file + "`\"")
	file.close()
	PyUtil.shell("chmod a+x " + file_name)

def genShellEnvScript():
	app_name    = PyConfig["APP_NAME"]
	install_dir = PyConfig["INSTALL_DIR"]

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

def mkDirs():
	print "====> Making directories..."
	for nix_dir in fishmake.NIXDirs:
		tnix_dir = PyDir.makeDirAbsolute(os.path.join(PyConfig["INSTALL_DIR"], nix_dir))
		if not os.path.exists(tnix_dir):
			os.makedirs(tnix_dir)
	print "====> Directories made..."

def installSystem():
	print "==> Preparing system..."
	steps = [mkDirs, genCookie, genConfigFile, genShellScript, genShellConnectScript, genShellEnvScript]
	for step in steps:
		step()
	print "==> System prepared!"

def installApps():
	for app in PyConfig["APP_DIRS"]:
		print "==> Installing app", os.path.basename(app)
		if not app in PyConfig["LANGUAGES"]:
			continue
		for compiler in PyConfig["LANGUAGES"][app]:
			print "====>", compiler.name
			compiler.install(app)
		installMisc(app)
		print "==>", os.path.basename(app), "installed!"

def installMisc(path):
	basename = os.path.basename(path)
	var_dir  = PyDir.makeDirAbsolute(os.path.join(path, "var"))
	doc_dir  = PyDir.makeDirAbsolute(os.path.join(path, "doc"))
	
	print "====> Installing documentation"
	## Install documentation
	if os.path.exists(doc_dir):
		install_doc_dir = PyDir.makeDirAbsolute(os.path.join(PyConfig["INSTALL_DIR"], "doc/" + basename + "-" + PyConfig["APP_VERSION"]))
		if os.path.exists(install_doc_dir):
			PyUtil.shell("rm -rf " + install_doc_dir)
		shutil.copytree(doc_dir, install_doc_dir)
	print "====> Documentation installed"

	print "====> Copying variable content..."
	if os.path.exists(var_dir):
		PyDir.copytree(var_dir, install_var_dir)
	print "====> Variable content copied!"

def installDependencies():
	pass
	#print "==> Installing dependencies"
	## Create the Dependencies
	#dep_dirs    = PyDir.findDirsByName("apps", "deps")
	#for dep_dir in dep_dirs:
	#	dep = os.path.basename(dep_dir)
	#	install_erl_dir = PyDir.makeDirAbsolute(os.path.join(PyConfig["INSTALL_DIR"], "lib/erlang/lib/" + dep))
	#
	#	## Create the erlang lib directory
	#	if not os.path.exists(install_erl_dir):
	#		os.makedirs(install_erl_dir)
	#
	#	print "==> Installing", dep
	#	## Clear conflicting versions
	#	if os.path.exists(install_erl_dir):
	#		PyUtil.shell("rm -rf " + install_erl_dir)
	#
	#	for erl_dir in fishmake.ErlDirs:
	#		src_dir = os.path.join(dep_dir, erl_dir)
	#		erl_dir = os.path.join(install_erl_dir, erl_dir)
	#		if os.path.exists(src_dir):
	#			shutil.copytree(src_dir, erl_dir)
	#
	#print "==> Dependencies installed"

def install():
	print "Installing", PyConfig["APP_NAME"]
	installSystem()
	installApps()
	installDependencies()
	