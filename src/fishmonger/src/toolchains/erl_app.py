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

		for mod in PyFind.findAllByPattern("*erl", self.app.srcDir()):
			(mod, x) = os.path.splitext(os.path.basename(mod))
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
		name      = app.name()
		
		file_src  = name + ".app.fish"
		file_name = name + ".app"
		
		app_src   = app.srcDir(  file=file_src)
		app_file  = app.buildDir(subdir="ebin", file=file_name)
		if os.path.isfile(app_src):
			doc   = ErlApp(app_src, app)
			doc.write(app_file)
		else:
			app_src = app.srcDir(file=file_name)
			if os.path.isfile(app_src):
				shutil.copyfile(app_src, app_file)

	def __init__(self):
		self.extensions = ["erl"]
		self.defaults   = {
			"TOOL_OPTIONS"      : {
				"ERL_MAIN"      : "",
				"EXECUTABLE"    : False
			}
		}

	def buildApp(self, child, app):
		return [self.genApp]

	def installApp(self, child, app):
		name      = app.name()
		file_name = name + ".app"
		src_file  = app.buildDir(subdir="ebin", file=file_name)
		dst_file  = app.installLangDir("erlang", subdir="ebin", file=file_name, app=True, version=True)
		PySH.copy(src_file, dst_file)

