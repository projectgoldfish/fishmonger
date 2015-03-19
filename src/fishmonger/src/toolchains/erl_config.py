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
	def genConfigFile(self, app):
		doc         = PyErl.PyErlDocument()
		expressions = PyErl.PyErlList()
		config_file = app.installEtcDir(file=app.name()+".erl_config.default")
		apps        = FishErl.getRequiredApps(app.name(), app.installDir())

		for t_app in apps:
			app_config = PyFind.find("*/" + t_app + ".erl_config", ".")
			if app_config and os.path.isfile(app_config):
				terms = PyErl.parse_file(app_config)
				expressions.appendChild(terms)

		doc.appendChild(expressions)

		PyErl.write_file(config_file, doc)

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
		main_steps = [self.genConfigFile]
		if app.name() == app["TOOL_OPTIONS"]["ERL_MAIN"] or ("EXECUTABLE" in app["APP_OPTIONS"] and app["APP_OPTIONS"]["EXECUTABLE"] == True):
			self.genConfigFile(app)

