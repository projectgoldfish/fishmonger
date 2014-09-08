from   pybase.config import Config as PyConfig
import pybase.config
import pyerl       as PyErl
import pybase.util as PyUtil
import os.path

def addVersion(app_src):
	arg_list = app_src.getElementsByTagName("list")[0]
	
	## If a vsn has already been specified leave it.
	for term in arg_list:
		if hasattr(term, '__iter__') and term[0].getValue == "vsn":
			return

	version_tuple = PyErl.PyErlTuple()
	version_tuple.appendChild(PyErl.PyErlAtom("vsn"))
	version_tuple.appendChild(PyErl.PyErlString(PyConfig["APP_VERSION"]))
	arg_list.appendChild(version_tuple)
	return app_src

def addId(app_src):
	arg_list = app_src.getElementsByTagName("list")[0]
	
	## If a vsn has already been specified leave it.
	for term in arg_list:
		if hasattr(term, '__iter__') and term[0].getValue == "id":
			return

	id_tuple = PyErl.PyErlTuple()
	id_tuple.appendChild(PyErl.PyErlAtom("id"))
	id_tuple.appendChild(PyErl.PyErlString(PyConfig["APP_ID"]))
	arg_list.appendChild(id_tuple)
	return app_src

## Looks in each app dir for a $APP.app.fish file
## uses it to generate a .app
def genApp(path, config):
	app      = os.path.basename(path)
	app_src  = os.path.join(path, "src/"  + app + ".app.fish")
	app_file = os.path.join(path, "ebin/" + app + ".app")
	
	print app_src

	if not os.path.isfile(app_src):
		return
	doc = PyErl.parse_file(app_src)

	## The .fish file is a base configuration.
	## We need to generate and append some default valeus to it
	## such as build number, and, uh, others to be determined...
	doc = addVersion(doc)
	doc = addId(doc)
	PyErl.write_file(app_file, doc)

def compiler(path):
	print "====> erlang"
	config = pybase.config.merge(PyConfig, pybase.config.parse(".fishmake.erl"))
	
	genApp(path, config)

	includes = " "
	for include in config["INCLUDE_DIRS"]:
		if include == "":
			continue
		includes += "-I " + include + " "

	output_dir = os.path.join(path, "ebin")
	cmd = "erlc " + includes + "-o " + output_dir + " " + os.path.join(path, "src/*.erl")
	return PyUtil.shell(cmd)