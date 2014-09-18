from   pybase.config import Config as PyConfig
import pybase.config
import pyerl       as PyErl
import pybase.util as PyUtil
import pybase.dir  as PyDir
import os.path
import shutil

## Directories found in a built erlang src dir.
dirs = ["ebin", "priv"]

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

def install(path):
	basename        = os.path.basename(path)
	install_erl_dir = PyDir.makeDirAbsolute(os.path.join(PyConfig["INSTALL_DIR"], "lib/erlang/lib/" + basename + "-" + PyConfig["APP_VERSION"]))
	
	print "====> Erlang"	
	print "======> Copying binaries..."
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
	print "======> Binaries copied!"

	return 0

def doc(path):
	pass

